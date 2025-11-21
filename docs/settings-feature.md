# Configuration Management for Classno (Pydantic Settings Alternative)

## Overview

This document outlines the plan for adding Pydantic Settings-like functionality to classno for application configuration management. This feature will enable loading configuration from environment variables, config files (JSON, YAML, TOML, .env), and other sources with full validation and type casting support.

## Goals

- **Drop-in replacement feel**: Similar API to pydantic-settings for easy adoption
- **Zero new dependencies**: Core functionality works with stdlib only
- **Optional enhancements**: YAML, TOML, .env support via optional dependencies
- **Leverages existing features**: Works seamlessly with `VALIDATION` and `LOSSY_AUTOCAST`
- **Flexible sources**: Pluggable system for custom configuration sources
- **Production-ready**: Secret handling, nested models, environment prefixes

## Architecture

### 1. New Feature Flag

Add `Features.SETTINGS` to `classno/constants.py`:

```python
class Features(enum.Flag):
    # ... existing features ...
    LOSSY_AUTOCAST = enum.auto()
    SETTINGS = enum.auto()  # NEW: Enable configuration loading

    # ... existing combinations ...
```

**Behavior**: When enabled, the class will automatically load values from configured sources during `__init__` before applying defaults.

### 2. Field Metadata Extensions

Extend `field(metadata={...})` to support configuration-specific metadata:

```python
class AppConfig(Classno):
    # Override env var name (default: APP_NAME or just NAME depending on prefix)
    app_name: str = field(metadata={"env": "APPLICATION_NAME"})

    # Mark as secret (hide in repr)
    password: str = field(metadata={"secret": True})

    # Alias for config file loading
    port: int = field(metadata={"alias": "server_port"})
```

**Supported metadata keys**:
- `"env"`: Override environment variable name
- `"secret"`: Mark sensitive data (excluded from repr)
- `"alias"`: Alternative name(s) when loading from files (string or list)

### 3. ConfigSource Abstraction

Create `classno/_config_sources.py` with a pluggable source system:

```python
from typing import Protocol, Any, Optional

class ConfigSource(Protocol):
    """Base protocol for configuration sources."""

    def get(self, key: str, *, field_hint: Any = None) -> tuple[bool, Any]:
        """
        Get a configuration value by key.

        Returns:
            (found, value): Tuple of (whether key was found, the value or None)
        """
        ...

    def has(self, key: str) -> bool:
        """Check if source has a value for the given key."""
        ...
```

**Built-in sources**:

```python
class EnvironmentSource:
    """Load from os.environ with optional prefix and case sensitivity."""
    def __init__(self, prefix: str = "", case_sensitive: bool = False):
        self.prefix = prefix
        self.case_sensitive = case_sensitive

class JsonSource:
    """Load from JSON file."""
    def __init__(self, path: str):
        self.path = path
        self.data = json.load(open(path))

class YamlSource:
    """Load from YAML file (requires PyYAML)."""
    def __init__(self, path: str):
        import yaml  # Optional dependency
        self.path = path
        self.data = yaml.safe_load(open(path))

class TomlSource:
    """Load from TOML file (requires tomli on Python <3.11)."""
    def __init__(self, path: str):
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            import tomli as tomllib
        self.path = path
        self.data = tomllib.load(open(path, 'rb'))

class DotEnvSource:
    """Load from .env file (requires python-dotenv)."""
    def __init__(self, path: str = ".env"):
        from dotenv import dotenv_values  # Optional dependency
        self.path = path
        self.data = dotenv_values(path)

class MultiSource:
    """Combine multiple sources with priority order."""
    def __init__(self, *sources: ConfigSource):
        self.sources = sources  # First source has highest priority
```

### 4. Settings Loader

Create `classno/_settings.py` with the main loading logic:

```python
def load_settings(obj: object, kwargs: dict) -> dict:
    """
    Load configuration from sources defined on the class.

    Priority (highest to lowest):
    1. Explicit kwargs passed to __init__
    2. Environment variables
    3. Config files
    4. Field defaults

    Args:
        obj: The Classno instance being initialized
        kwargs: Keyword arguments passed to __init__

    Returns:
        Merged configuration dictionary
    """
    cls = type(obj)
    fields = cls.__fields__

    # Get sources from class attributes
    sources = getattr(cls, '__config_sources__', None)
    if sources is None:
        # Default sources
        env_prefix = getattr(cls, '__env_prefix__', "")
        case_sensitive = getattr(cls, '__case_sensitive__', False)
        sources = [EnvironmentSource(prefix=env_prefix, case_sensitive=case_sensitive)]

        # Add config file if specified
        config_file = getattr(cls, '__config_file__', None)
        if config_file and os.path.exists(config_file):
            sources.append(_get_file_source(config_file))

    # Load from sources
    config = {}
    for field_name, field in fields.items():
        if field_name in kwargs:
            continue  # Explicit kwarg takes precedence

        # Determine key to look up
        env_override = field.metadata.get("env")
        if env_override:
            keys = [env_override]
        else:
            keys = [field_name]
            # Add alias variations
            if "alias" in field.metadata:
                alias = field.metadata["alias"]
                keys.extend([alias] if isinstance(alias, str) else alias)

        # Try each source in order
        for source in sources:
            for key in keys:
                found, value = source.get(key, field_hint=field.hint)
                if found:
                    config[field_name] = value
                    break
            if field_name in config:
                break

    return {**config, **kwargs}  # kwargs override everything
```

### 5. Class-Level Configuration

Support special class attributes to configure settings behavior:

```python
class Settings(Classno):
    __features__ = Features.SETTINGS | Features.VALIDATION

    # Optional configuration
    __env_prefix__ = "APP_"              # Prefix for env vars: APP_DEBUG, APP_PORT, etc.
    __config_file__ = "config.json"      # Default config file to load
    __case_sensitive__ = False           # Case-insensitive env var matching
    __config_sources__ = [...]           # Custom sources (overrides defaults)
```

**Class attributes**:
- `__env_prefix__`: Prefix added to all env var names (default: `""`)
- `__config_file__`: Path to config file (auto-detected format)
- `__case_sensitive__`: Whether env var matching is case-sensitive (default: `False`)
- `__config_sources__`: Custom list of ConfigSource objects (overrides defaults)

### 6. Integration with Hook System

Add settings handler to `classno/_feature_handlers.py`:

```python
def settings_obj_handler(obj: object) -> None:
    """Apply settings loading to object during initialization."""
    from classno import _settings
    _settings.apply_loaded_settings(obj)

# Add to object handlers map
_OBJECT_HANDLERS_MAP: dict[c.Features, t.Callable[[object], None]] = {
    c.Features.LOSSY_AUTOCAST: lossy_autocast_obj_handler,
    c.Features.VALIDATION: validation_obj_handler,
    c.Features.SETTINGS: settings_obj_handler,  # NEW
}
```

**Processing order**: Settings loading happens in `__init__` hook BEFORE field initialization, so loaded values are available as if they were passed as kwargs.

## Implementation Steps

### Phase 1: Core Infrastructure (Day 1-2)
1. Add `Features.SETTINGS` flag to `constants.py`
2. Create `_config_sources.py` with `ConfigSource` protocol
3. Implement `EnvironmentSource` (no dependencies)
4. Create basic structure of `_settings.py`

### Phase 2: Environment Variables (Day 2-3)
1. Implement env var name resolution logic
2. Add prefix support (`__env_prefix__`)
3. Add case-insensitive matching
4. Support field metadata `"env"` override
5. Write unit tests for env var loading

### Phase 3: File Sources (Day 3-4)
1. Implement `JsonSource` (stdlib `json`)
2. Implement `DotEnvSource` with graceful fallback
3. Implement `YamlSource` with graceful fallback
4. Implement `TomlSource` with Python 3.11+ support
5. Add file format auto-detection helper
6. Write unit tests for each file source

### Phase 4: Integration & Advanced Features (Day 5-6)
1. Implement `load_settings()` with source priority
2. Add settings handler to feature handlers
3. Integrate with `__init__` hook
4. Support nested Classno models (recursive loading)
5. Implement secret field handling (hide in repr)
6. Add `MultiSource` for custom source combinations

### Phase 5: Testing (Day 6-7)
1. Unit tests for each source type
2. Integration tests for multi-source scenarios
3. Test priority order (kwargs > env > file > defaults)
4. Test nested models
5. Test secret fields
6. Test edge cases (missing files, invalid values, etc.)
7. Regression tests (ensure existing features work)

### Phase 6: Documentation & Examples (Day 8)
1. Add docstrings to all public APIs
2. Create `examples/settings_example.py`
3. Update main README with settings section
4. Create migration guide from pydantic-settings
5. Document optional dependencies

## Usage Examples

### Basic Example

```python
from classno import Classno, Features, field

class AppConfig(Classno):
    __features__ = Features.SETTINGS | Features.VALIDATION
    __env_prefix__ = "APP_"

    name: str = field(default="MyApp")
    debug: bool = field(default=False)
    port: int = field(default=8000)

# With environment: APP_DEBUG=true APP_PORT=3000
config = AppConfig()
print(config.debug)  # True (from env)
print(config.port)   # 3000 (from env)
print(config.name)   # "MyApp" (default)

# Or override explicitly
config = AppConfig(name="CustomApp", port=5000)
print(config.name)   # "CustomApp" (explicit)
print(config.port)   # 5000 (explicit)
```

### File-Based Configuration

```python
# config.json:
# {
#   "app_name": "Production App",
#   "database": {
#     "host": "db.example.com",
#     "port": 5432
#   }
# }

class DatabaseConfig(Classno):
    __features__ = Features.SETTINGS
    host: str
    port: int = field(default=5432)

class Settings(Classno):
    __features__ = Features.SETTINGS | Features.VALIDATION
    __config_file__ = "config.json"

    app_name: str = field(metadata={"alias": "app_name"})
    database: DatabaseConfig = field(default_factory=DatabaseConfig)

settings = Settings()
print(settings.app_name)           # "Production App"
print(settings.database.host)      # "db.example.com"
```

### Secret Fields

```python
class DatabaseConfig(Classno):
    __features__ = Features.SETTINGS
    __env_prefix__ = "DB_"

    host: str
    password: str = field(metadata={"secret": True})
    port: int = field(default=5432)

# With environment: DB_HOST=localhost DB_PASSWORD=secret123
config = DatabaseConfig()
print(repr(config))
# DatabaseConfig(host='localhost', password='***', port=5432)
# Password is hidden in repr but accessible via config.password
```

### Custom Sources

```python
from classno._config_sources import ConfigSource, MultiSource

class RedisSource:
    """Load config from Redis."""
    def __init__(self, redis_client, key_prefix="config:"):
        self.redis = redis_client
        self.prefix = key_prefix

    def get(self, key: str, *, field_hint=None) -> tuple[bool, Any]:
        value = self.redis.get(f"{self.prefix}{key}")
        if value is None:
            return False, None
        return True, value.decode()

    def has(self, key: str) -> bool:
        return self.redis.exists(f"{self.prefix}{key}")

class Settings(Classno):
    __features__ = Features.SETTINGS
    __config_sources__ = [
        RedisSource(redis_client),  # Highest priority
        EnvironmentSource(),
        JsonSource("config.json"),  # Lowest priority
    ]

    feature_flags: dict = field(default_factory=dict)
```

### Nested Configuration

```python
class ServerConfig(Classno):
    __features__ = Features.SETTINGS
    host: str = field(default="0.0.0.0")
    port: int = field(default=8000)

class DatabaseConfig(Classno):
    __features__ = Features.SETTINGS
    url: str = field(metadata={"env": "DATABASE_URL"})

class Settings(Classno):
    __features__ = Features.SETTINGS | Features.VALIDATION
    __env_prefix__ = "APP_"

    server: ServerConfig = field(default_factory=ServerConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)

# Environment:
# APP_SERVER_HOST=api.example.com
# APP_SERVER_PORT=9000
# DATABASE_URL=postgresql://localhost/mydb

settings = Settings()
print(settings.server.host)      # "api.example.com"
print(settings.database.url)     # "postgresql://localhost/mydb"
```

## Dependencies

### Required (Stdlib)
- `os` - Environment variable access
- `json` - JSON config files
- `pathlib` - File path handling
- `typing` - Type hints and protocols

### Optional
- `python-dotenv` - For `.env` file support
- `PyYAML` - For YAML config files
- `tomli` - For TOML support on Python <3.11 (`tomllib` is stdlib in 3.11+)

**Graceful degradation**: If optional dependencies are missing, the specific source will raise a clear error with installation instructions when attempted to be used.

## Compatibility

- **Python version**: 3.10+ (matches existing requirement)
- **Breaking changes**: None - feature is opt-in via `Features.SETTINGS`
- **Feature interaction**:
  - Works with `VALIDATION` - loaded values are validated
  - Works with `LOSSY_AUTOCAST` - env vars (strings) are auto-cast to target types
  - Works with `FROZEN` - loaded values set during init, then frozen
  - Works with `PRIVATE` - private fields can be loaded from config

## Open Questions & Decisions

### 1. Auto-load on init vs explicit load?

**Option A**: Auto-load when `Features.SETTINGS` is enabled (Pydantic style)
```python
config = Settings()  # Automatically loads from sources
```

**Option B**: Require explicit load call
```python
config = Settings.load()  # Explicit
```

**Decision**: **Option A** - Auto-load for better DX and pydantic-settings compatibility.

### 2. Reload/refresh mechanism?

Support runtime config reloading for long-running applications?

```python
settings.reload()  # Re-read from sources
# or
settings = Settings.reload()  # Return new instance
```

**Decision**: **Defer to later** - Start simple, add if users request it.

### 3. Export/dump configuration?

Support writing config back to files?

```python
settings.to_json("config.json")
settings.to_env(".env")
```

**Decision**: **Defer to later** - Focus on loading first, add export if needed.

### 4. Class-level validation?

Validate required fields at class definition time vs runtime?

```python
class Settings(Classno):
    __features__ = Features.SETTINGS
    required_field: str  # No default - should this error at class definition?
```

**Decision**: **Runtime validation** - Same as current Classno behavior, error during `__init__` if not provided.

### 5. Nested field path syntax?

Support loading nested values from flat sources like env vars?

```python
# Environment: APP_DATABASE_HOST=localhost
class Settings(Classno):
    database: DatabaseConfig  # Should this auto-detect nested path?
```

**Decision**: **Yes, with prefix propagation** - Nested models inherit parent prefix + their field name: `APP_DATABASE_HOST`

## Future Enhancements

### Configuration Validation
- Pre-load validation (check required fields before app starts)
- Custom validators per field
- Cross-field validation

### Advanced Sources
- AWS Parameter Store / Secrets Manager
- Azure Key Vault
- Google Cloud Secret Manager
- Consul / etcd
- Vault (HashiCorp)

### Developer Experience
- Config documentation auto-generation
- Environment variable documentation
- Config diff tool (compare runtime vs defaults)
- Config migration tools

### Performance
- Lazy loading for expensive sources
- Cache configuration to avoid repeated source access
- Async source support for I/O-bound operations

## Success Metrics

1. **API Compatibility**: Easy migration from pydantic-settings (< 10 lines changed)
2. **Zero Dependencies**: Core features work with stdlib only
3. **Performance**: < 1ms overhead for simple config loading
4. **Test Coverage**: 95%+ coverage for settings module
5. **Documentation**: Complete examples for common use cases

## References

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [python-decouple](https://github.com/HBNetwork/python-decouple) - Similar lightweight alternative
- [dynaconf](https://www.dynaconf.com/) - Feature-rich configuration library
