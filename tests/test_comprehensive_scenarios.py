from datetime import datetime
from typing import Optional
from typing import Union

import pytest

from classno import Classno
from classno import Features
from classno import field
from classno.exceptions import ValidationError


class TestComprehensiveScenarios:
    """Comprehensive test scenarios covering real-world usage patterns."""

    def test_real_world_user_model(self):
        """Test a realistic user model with various features."""

        class User(Classno):
            __features__ = Features.VALIDATION | Features.FROZEN

            id: int
            username: str
            email: str
            is_active: bool = True
            tags: list[str] = field(default_factory=list)
            metadata: dict[str, Union[str, int]] = field(default_factory=dict)
            created_at: Optional[datetime] = None

        # Valid user creation
        user = User(
            id=1,
            username="john_doe",
            email="john@example.com",
            tags=["admin", "developer"],
            metadata={"department": "engineering", "level": 5},
            created_at=datetime.now(),
        )

        assert user.id == 1
        assert user.username == "john_doe"
        assert user.is_active is True
        assert len(user.tags) == 2
        assert user.metadata["level"] == 5

        # Should be frozen
        with pytest.raises(Exception):
            user.username = "changed"

        # Should validate
        with pytest.raises(ValidationError):
            User(id="invalid", username="test", email="test@example.com")

    def test_nested_business_model(self):
        """Test complex nested business model."""

        class Address(Classno):
            street: str
            city: str
            state: str
            zip_code: str

        class Company(Classno):
            __features__ = Features.VALIDATION

            name: str
            address: Address
            employees: list[str] = field(default_factory=list)
            founded_year: int
            is_public: bool = False

        class Employee(Classno):
            __features__ = Features.VALIDATION | Features.HASH
            __hash_keys__ = {"employee_id"}

            employee_id: str
            full_name: str
            company: Company
            salary: Optional[int] = None
            departments: list[str] = field(default_factory=list)

        # Create nested structure
        address = Address(
            street="123 Business Ave",
            city="San Francisco",
            state="CA",
            zip_code="94101",
        )

        company = Company(
            name="Tech Corp",
            address=address,
            employees=["EMP001", "EMP002"],
            founded_year=2010,
            is_public=True,
        )

        employee = Employee(
            employee_id="EMP001",
            full_name="John Doe",
            company=company,
            salary=120000,
            departments=["Engineering", "Research"],
        )

        # Verify deep nesting works
        assert employee.company.name == "Tech Corp"
        assert employee.company.address.city == "San Francisco"
        assert employee.company.is_public is True
        assert "Engineering" in employee.departments

        # Should be hashable based on employee_id
        hash_val = hash(employee)
        assert isinstance(hash_val, int)

    def test_configuration_management(self):
        """Test configuration management scenario with defaults and validation."""

        class DatabaseConfig(Classno):
            __features__ = Features.VALIDATION | Features.FROZEN

            host: str = "localhost"
            port: int = 5432
            database: str
            username: str
            password: str
            ssl_enabled: bool = True
            connection_pool_size: int = 10
            timeout: float = 30.0

        class AppConfig(Classno):
            __features__ = Features.VALIDATION | Features.FROZEN

            app_name: str
            debug: bool = False
            database: DatabaseConfig
            allowed_hosts: list[str] = field(default_factory=list)
            feature_flags: dict[str, bool] = field(default_factory=dict)
            log_level: str = "INFO"

        # Create configuration with some defaults
        db_config = DatabaseConfig(
            database="myapp", username="dbuser", password="secret123"
        )

        app_config = AppConfig(
            app_name="MyApplication",
            database=db_config,
            allowed_hosts=["localhost", "127.0.0.1"],
            feature_flags={"new_ui": True, "beta_features": False},
        )

        # Verify defaults are applied
        assert app_config.debug is False
        assert app_config.log_level == "INFO"
        assert app_config.database.host == "localhost"
        assert app_config.database.port == 5432
        assert app_config.database.ssl_enabled is True

        # Should be frozen
        with pytest.raises(Exception):
            app_config.debug = True

        with pytest.raises(Exception):
            app_config.database.host = "remote.db.com"

    def test_api_response_modeling(self):
        """Test API response modeling with optional fields and unions."""

        class ApiError(Classno):
            code: int
            message: str
            details: Optional[dict[str, str]] = None

        class PaginationMeta(Classno):
            page: int
            per_page: int
            total: int
            has_next: bool
            has_prev: bool

        class ApiResponse(Classno):
            __features__ = Features.VALIDATION

            success: bool
            data: Optional[Union[dict, list]] = None
            error: Optional[ApiError] = None
            meta: Optional[PaginationMeta] = None
            timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

        # Successful response
        success_response = ApiResponse(
            success=True,
            data={"users": [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]},
            meta=PaginationMeta(
                page=1, per_page=10, total=25, has_next=True, has_prev=False
            ),
        )

        assert success_response.success is True
        assert success_response.error is None
        assert success_response.meta.total == 25
        assert success_response.meta.has_next is True

        # Error response
        error_response = ApiResponse(
            success=False,
            error=ApiError(
                code=404,
                message="User not found",
                details={"resource": "user", "id": "123"},
            ),
        )

        assert error_response.success is False
        assert error_response.data is None
        assert error_response.error.code == 404
        assert error_response.error.details["resource"] == "user"

    def test_autocasting_scenarios(self):
        """Test realistic autocasting scenarios."""

        class FlexibleData(Classno):
            __features__ = Features.LOSSY_AUTOCAST

            id: str  # Should convert numbers to strings
            score: int  # Should truncate floats
            percentage: float  # Should convert integers
            is_enabled: str  # Should convert booleans to strings
            tags: list  # Should convert other iterables

        data = FlexibleData(
            id=12345,
            score=87.9,
            percentage=75,
            is_enabled=True,
            tags={"python", "web", "api"},  # set to list
        )

        assert data.id == "12345"
        assert data.score == 87  # Truncated
        assert data.percentage == 75.0
        assert data.is_enabled == "True"
        assert isinstance(data.tags, list)
        assert len(data.tags) == 3

    def test_inheritance_with_mixins(self):
        """Test inheritance patterns with mixin-like functionality."""

        class TimestampMixin(Classno):
            created_at: Optional[datetime] = None
            updated_at: Optional[datetime] = None

        class AuditMixin(Classno):
            created_by: Optional[str] = None
            modified_by: Optional[str] = None

        class BaseModel(TimestampMixin, AuditMixin):
            __features__ = Features.VALIDATION
            id: int

        class BlogPost(BaseModel):
            title: str
            content: str
            published: bool = False
            tags: list[str] = field(default_factory=list)

        # Create blog post with inherited fields
        post = BlogPost(
            id=1,
            title="My First Post",
            content="This is the content of my first blog post.",
            published=True,
            tags=["python", "programming"],
            created_at=datetime.now(),
            created_by="author@example.com",
        )

        assert post.id == 1
        assert post.title == "My First Post"
        assert post.published is True
        assert post.created_by == "author@example.com"
        assert post.updated_at is None  # Not set
        assert isinstance(post.created_at, datetime)

    def test_complex_validation_scenarios(self):
        """Test complex validation scenarios."""

        class Product(Classno):
            __features__ = Features.VALIDATION

            name: str
            price: float
            categories: list[str]
            specifications: dict[str, Union[str, int, float]]
            availability: dict[str, int]  # region -> stock count
            metadata: dict[str, Optional[str]] = field(default_factory=dict)

        # Valid product
        product = Product(
            name="Laptop Computer",
            price=999.99,
            categories=["electronics", "computers"],
            specifications={
                "cpu": "Intel i7",
                "ram": 16,
                "storage": 512,
                "weight": 2.5,
            },
            availability={"US": 10, "EU": 5, "Asia": 0},
            metadata={"warranty": "2 years", "brand": "TechBrand"},
        )

        assert product.name == "Laptop Computer"
        assert product.specifications["ram"] == 16
        assert product.availability["US"] == 10

        # Invalid validation scenarios
        with pytest.raises(ValidationError):
            Product(
                name=123,  # Should be string
                price=999.99,
                categories=["electronics"],
                specifications={},
                availability={},
            )

    def test_factory_defaults_complex(self):
        """Test complex factory default scenarios."""

        def create_default_settings():
            return {
                "theme": "dark",
                "language": "en",
                "notifications": True,
                "privacy": {"analytics": False, "cookies": True},
            }

        def create_empty_stats():
            return {"views": 0, "likes": 0, "shares": 0}

        class UserProfile(Classno):
            username: str
            settings: dict = field(default_factory=create_default_settings)
            stats: dict[str, int] = field(default_factory=create_empty_stats)
            bookmarks: list[str] = field(default_factory=list)
            created_at: datetime = field(default_factory=datetime.now)

        # Create multiple instances to test factory functions
        profile1 = UserProfile(username="user1")
        profile2 = UserProfile(username="user2")

        # Should have independent default objects
        assert profile1.settings is not profile2.settings
        assert profile1.stats is not profile2.stats
        assert profile1.bookmarks is not profile2.bookmarks

        # But should have same default values
        assert profile1.settings["theme"] == "dark"
        assert profile2.settings["theme"] == "dark"
        assert profile1.stats["views"] == 0
        assert profile2.stats["views"] == 0

        # Modifications should be independent
        profile1.settings["theme"] = "light"
        profile1.stats["views"] = 100

        assert profile1.settings["theme"] == "light"
        assert profile2.settings["theme"] == "dark"  # Unchanged
        assert profile1.stats["views"] == 100
        assert profile2.stats["views"] == 0  # Unchanged

    def test_edge_case_empty_and_none(self):
        """Test edge cases with empty values and None."""

        class EdgeCaseModel(Classno):
            __features__ = Features.VALIDATION

            required_string: str
            optional_string: Optional[str] = None
            empty_list: list[str] = field(default_factory=list)
            empty_dict: dict[str, int] = field(default_factory=dict)
            nullable_list: Optional[list[int]] = None

        # Test with minimal values
        model = EdgeCaseModel(required_string="")
        assert model.required_string == ""
        assert model.optional_string is None
        assert model.empty_list == []
        assert model.empty_dict == {}
        assert model.nullable_list is None

        # Test with actual values
        model2 = EdgeCaseModel(
            required_string="test",
            optional_string="optional",
            empty_list=["a", "b"],
            empty_dict={"key": 42},
            nullable_list=[1, 2, 3],
        )
        assert model2.optional_string == "optional"
        assert model2.empty_list == ["a", "b"]
        assert model2.empty_dict == {"key": 42}
        assert model2.nullable_list == [1, 2, 3]

    def test_performance_with_many_fields(self):
        """Test performance characteristics with many fields."""

        class ManyFieldsModel(Classno):
            # Create a model with many fields to test performance
            field_01: str = "default"
            field_02: int = 0
            field_03: float = 0.0
            field_04: bool = False
            field_05: list[str] = field(default_factory=list)
            field_06: dict[str, int] = field(default_factory=dict)
            field_07: Optional[str] = None
            field_08: str = "default"
            field_09: int = 0
            field_10: float = 0.0
            field_11: bool = False
            field_12: list[int] = field(default_factory=list)
            field_13: dict[str, str] = field(default_factory=dict)
            field_14: Optional[int] = None
            field_15: str = "default"

        # Should handle many fields efficiently
        obj = ManyFieldsModel(field_01="test", field_02=42, field_03=3.14)
        assert obj.field_01 == "test"
        assert obj.field_02 == 42
        assert obj.field_03 == 3.14
        assert obj.field_04 is False  # Default
        assert obj.field_05 == []  # Factory default
