import pytest
from typing import List, Dict, Tuple, Optional, Union
from datetime import datetime

import classno
from classno import Classno, Features, field
from classno.exceptions import ValidationError


class TestComplexNestedStructures:
    """Test complex nested object structures and compositions."""

    def test_basic_nested_objects(self):
        """Test basic nested Classno objects."""
        class Address(Classno):
            street: str
            city: str
            country: str = "USA"
            zip_code: Optional[str] = None

        class Person(Classno):
            name: str
            age: int
            address: Address

        # Create nested structure
        address = Address(street="123 Main St", city="Boston", zip_code="02101")
        person = Person(name="John", age=30, address=address)

        assert person.name == "John"
        assert person.age == 30
        assert person.address.street == "123 Main St"
        assert person.address.city == "Boston"
        assert person.address.country == "USA"
        assert person.address.zip_code == "02101"

    def test_deeply_nested_structures(self):
        """Test deeply nested structures with multiple levels."""
        class ContactInfo(Classno):
            email: str
            phone: Optional[str] = None

        class Address(Classno):
            street: str
            city: str
            state: str
            postal_code: str

        class Person(Classno):
            first_name: str
            last_name: str
            contact: ContactInfo
            address: Address

        class Company(Classno):
            name: str
            employees: List[Person]
            headquarters: Address

        class Department(Classno):
            name: str
            manager: Person
            company: Company

        # Build up the nested structure
        contact = ContactInfo(email="john@example.com", phone="555-1234")
        address = Address(street="123 Main St", city="Boston", state="MA", postal_code="02101")
        manager = Person(first_name="John", last_name="Doe", contact=contact, address=address)

        emp_contact = ContactInfo(email="jane@example.com")
        emp_address = Address(street="456 Oak Ave", city="Cambridge", state="MA", postal_code="02138")
        employee = Person(first_name="Jane", last_name="Smith", contact=emp_contact, address=emp_address)

        hq_address = Address(street="789 Corporate Blvd", city="Boston", state="MA", postal_code="02102")
        company = Company(name="Tech Corp", employees=[manager, employee], headquarters=hq_address)

        department = Department(name="Engineering", manager=manager, company=company)

        # Verify deep access
        assert department.name == "Engineering"
        assert department.manager.first_name == "John"
        assert department.manager.contact.email == "john@example.com"
        assert department.company.name == "Tech Corp"
        assert len(department.company.employees) == 2
        assert department.company.employees[0].last_name == "Doe"
        assert department.company.employees[1].contact.email == "jane@example.com"
        assert department.company.headquarters.city == "Boston"

    def test_nested_with_validation(self):
        """Test nested structures with validation enabled."""
        class Coordinate(Classno):
            __features__ = Features.VALIDATION
            x: float
            y: float
            z: float = 0.0

        class Route(Classno):
            __features__ = Features.VALIDATION
            name: str
            waypoints: List[Coordinate]
            metadata: Dict[str, Union[str, int]]

        class Journey(Classno):
            __features__ = Features.VALIDATION
            title: str
            routes: List[Route]
            start_time: Optional[datetime] = None

        # Valid nested structure with validation
        coord1 = Coordinate(x=10.5, y=20.3, z=5.0)
        coord2 = Coordinate(x=15.7, y=25.8)
        route = Route(
            name="Main Route",
            waypoints=[coord1, coord2],
            metadata={"distance": 100, "difficulty": "easy"}
        )
        journey = Journey(title="Mountain Hike", routes=[route])

        assert journey.title == "Mountain Hike"
        assert len(journey.routes) == 1
        assert journey.routes[0].name == "Main Route"
        assert len(journey.routes[0].waypoints) == 2
        assert journey.routes[0].waypoints[0].x == 10.5
        assert journey.routes[0].metadata["distance"] == 100

        # Should validate nested structures
        with pytest.raises(ValidationError):
            invalid_coord = Coordinate(x="invalid", y=20.3)
        
        with pytest.raises(ValidationError):
            Route(name="test", waypoints=["invalid waypoint"], metadata={})

    def test_nested_collections(self):
        """Test nested collections of objects."""
        class Tag(Classno):
            name: str
            color: str = "blue"

        class Category(Classno):
            name: str
            tags: List[Tag]

        class Article(Classno):
            title: str
            content: str
            categories: List[Category]
            metadata: Dict[str, Union[str, List[str]]]

        class Blog(Classno):
            name: str
            articles: List[Article]
            categories: List[Category]

        # Create complex nested collections
        tech_tags = [Tag(name="Python", color="yellow"), Tag(name="AI", color="green")]
        science_tags = [Tag(name="Research", color="red"), Tag(name="Data", color="purple")]

        tech_category = Category(name="Technology", tags=tech_tags)
        science_category = Category(name="Science", tags=science_tags)

        article1 = Article(
            title="Python AI Tutorial",
            content="Learn AI with Python...",
            categories=[tech_category],
            metadata={"author": "John Doe", "keywords": ["python", "ai", "tutorial"]}
        )

        article2 = Article(
            title="Data Science Research",
            content="Latest in data science...",
            categories=[science_category, tech_category],
            metadata={"author": "Jane Smith", "keywords": ["data", "science"]}
        )

        blog = Blog(
            name="Tech Blog",
            articles=[article1, article2],
            categories=[tech_category, science_category]
        )

        # Verify complex nested access
        assert blog.name == "Tech Blog"
        assert len(blog.articles) == 2
        assert blog.articles[0].title == "Python AI Tutorial"
        assert len(blog.articles[0].categories) == 1
        assert len(blog.articles[0].categories[0].tags) == 2
        assert blog.articles[0].categories[0].tags[0].name == "Python"
        assert blog.articles[0].categories[0].tags[0].color == "yellow"
        assert blog.articles[1].categories[1].tags[1].name == "AI"

    def test_cyclic_references(self):
        """Test handling of cyclic references in nested structures."""
        class Node(Classno):
            value: str
            children: List['Node'] = field(default_factory=list)
            parent: Optional['Node'] = None

        # Create a tree structure
        root = Node(value="root")
        child1 = Node(value="child1", parent=root)
        child2 = Node(value="child2", parent=root)
        grandchild = Node(value="grandchild", parent=child1)

        root.children = [child1, child2]
        child1.children = [grandchild]

        # Verify the structure
        assert root.value == "root"
        assert len(root.children) == 2
        assert root.children[0].value == "child1"
        assert root.children[0].parent.value == "root"
        assert root.children[1].value == "child2"
        assert len(root.children[0].children) == 1
        assert root.children[0].children[0].value == "grandchild"
        assert root.children[0].children[0].parent.value == "child1"

    def test_nested_immutable_structures(self):
        """Test nested structures with immutable features."""
        class ImmutablePoint(Classno):
            __features__ = Features.IMMUTABLE
            x: float
            y: float

        class ImmutableShape(Classno):
            __features__ = Features.IMMUTABLE
            name: str
            points: List[ImmutablePoint]
            area: float

        # Create immutable nested structure
        points = [
            ImmutablePoint(x=0.0, y=0.0),
            ImmutablePoint(x=10.0, y=0.0),
            ImmutablePoint(x=10.0, y=10.0),
            ImmutablePoint(x=0.0, y=10.0)
        ]
        shape = ImmutableShape(name="Square", points=points, area=100.0)

        # Verify immutability
        with pytest.raises(Exception):
            shape.name = "Changed"
        
        with pytest.raises(Exception):
            shape.points[0].x = 5.0

    def test_nested_with_custom_comparison(self):
        """Test nested structures with custom comparison keys."""
        class PersonWithId(Classno):
            __hash_keys__ = {"id"}
            __eq_keys__ = {"id"}
            __order_keys__ = {"name"}

            id: int
            name: str
            age: int

        class Team(Classno):
            __eq_keys__ = {"name", "members"}
            
            name: str
            members: List[PersonWithId]

        person1 = PersonWithId(id=1, name="Alice", age=25)
        person2 = PersonWithId(id=2, name="Bob", age=30)
        person3 = PersonWithId(id=1, name="Alice Updated", age=26)  # Same ID as person1

        team1 = Team(name="Team A", members=[person1, person2])
        team2 = Team(name="Team A", members=[person3, person2])  # person3 has same ID as person1

        # person1 and person3 should be equal based on ID
        assert person1 == person3

        # Teams should be equal because they have same name and equivalent members
        assert team1 == team2

    def test_complex_nested_factory_defaults(self):
        """Test nested structures with complex default factories."""
        class Settings(Classno):
            debug: bool = False
            max_connections: int = 100
            features: List[str] = field(default_factory=list)

        class Database(Classno):
            host: str = "localhost"
            port: int = 5432
            settings: Settings = field(default_factory=Settings)

        class Application(Classno):
            name: str
            databases: Dict[str, Database] = field(default_factory=dict)
            global_settings: Settings = field(default_factory=Settings)

        # Create with defaults
        app = Application(name="MyApp")
        assert app.name == "MyApp"
        assert app.databases == {}
        assert app.global_settings.debug is False
        assert app.global_settings.max_connections == 100

        # Add database with defaults
        app.databases["primary"] = Database()
        assert app.databases["primary"].host == "localhost"
        assert app.databases["primary"].port == 5432
        assert app.databases["primary"].settings.debug is False

        # Add configured database
        custom_settings = Settings(debug=True, max_connections=200, features=["caching", "logging"])
        app.databases["secondary"] = Database(host="remote", port=3306, settings=custom_settings)
        
        assert app.databases["secondary"].host == "remote"
        assert app.databases["secondary"].settings.debug is True
        assert app.databases["secondary"].settings.features == ["caching", "logging"]

    def test_nested_optional_chains(self):
        """Test nested optional chains and None handling."""
        class Profile(Classno):
            bio: Optional[str] = None
            avatar_url: Optional[str] = None

        class SocialLinks(Classno):
            twitter: Optional[str] = None
            linkedin: Optional[str] = None

        class User(Classno):
            username: str
            profile: Optional[Profile] = None
            social: Optional[SocialLinks] = None

        class Organization(Classno):
            name: str
            owner: Optional[User] = None
            members: List[User] = field(default_factory=list)

        # Test with all None optionals
        user1 = User(username="user1")
        assert user1.username == "user1"
        assert user1.profile is None
        assert user1.social is None

        # Test with some optionals filled
        profile = Profile(bio="Developer", avatar_url="http://example.com/avatar.jpg")
        user2 = User(username="user2", profile=profile)
        assert user2.profile.bio == "Developer"
        assert user2.social is None

        # Test organization with optional owner
        org1 = Organization(name="Org1")
        assert org1.name == "Org1"
        assert org1.owner is None
        assert org1.members == []

        org2 = Organization(name="Org2", owner=user2, members=[user1, user2])
        assert org2.owner.username == "user2"
        assert org2.owner.profile.bio == "Developer"
        assert len(org2.members) == 2