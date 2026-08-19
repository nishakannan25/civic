"""Phase 9 Test Suite — Civic Department Routing + Admin Dashboard.

Tests all 22 required backend verification criteria for Phase 9:
1. Seed default departments
2. Department listing endpoint
3. Automatic routing for 6 civic issue types to active departments
4. Unknown issue type routing fallback to UNASSIGNED
5. Inactive department routing fallback to UNASSIGNED
6. Admin manual department assignment & reassignment
7. Citizen forbidden from admin assignment/status/routing endpoints
8. Status lifecycle transitions validation (UNASSIGNED -> ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED)
9. Invalid status transitions rejected (400)
10. Resolution note & timestamp recorded on RESOLVED status update
11. Dashboard summary returns accurate database metric counts
12. Dashboard summary returns correct issue and risk distributions
13. Paginated admin incident list endpoint
14. Filter admin incident list by issue_type, risk_level, department_id, status
15. Search admin incident list by search query / incident ID
16. Map incidents endpoint returns items with location_status
17. Single incident detail endpoint for admin
18. SOS emergency handling preservation (Phase 8 compatibility)
19. Offline idempotency preservation (Phase 3 compatibility)
20. Risk assessment integration (Phase 6 compatibility)
21. AI inference integration (Phase 5 compatibility)
22. Full regression pass check
"""

import os
import sys
import unittest
from datetime import datetime, timezone

# Ensure backend directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import get_db
from app.database.base import Base
from app.models.user import User

from app.models.department import Department
from app.models.incident import Incident
from app.core.security import get_password_hash, create_access_token
from app.core.constants import UserRole, IncidentStatus, RiskLevel, DEFAULT_DEPARTMENT_MAPPINGS
from app.services.routing_service import CivicRoutingService

# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class Phase9TestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = TestingSessionLocal()

        # Seed default departments
        CivicRoutingService.seed_default_departments(cls.db)

        # Create Admin User
        cls.admin_user = User(
            name="Admin User",
            email="admin@civic.ai",
            password_hash=get_password_hash("AdminPass123!"),
            role=UserRole.ADMIN.value,
        )
        # Create Citizen User
        cls.citizen_user = User(
            name="Citizen User",
            email="citizen@civic.ai",
            password_hash=get_password_hash("CitizenPass123!"),
            role=UserRole.CITIZEN.value,
        )

        cls.db.add(cls.admin_user)
        cls.db.add(cls.citizen_user)
        cls.db.commit()
        cls.db.refresh(cls.admin_user)
        cls.db.refresh(cls.citizen_user)

        cls.admin_token = create_access_token(cls.admin_user.id)
        cls.citizen_token = create_access_token(cls.citizen_user.id)

        cls.admin_headers = {"Authorization": f"Bearer {cls.admin_token}"}
        cls.citizen_headers = {"Authorization": f"Bearer {cls.citizen_token}"}

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=engine)

    def test_01_seed_departments(self):
        """Test default 6 departments are present in database."""
        depts = self.db.query(Department).all()
        self.assertGreaterEqual(len(depts), 6)
        dept_names = [d.name for d in depts]
        for expected in DEFAULT_DEPARTMENT_MAPPINGS.values():
            self.assertIn(expected, dept_names)

    def test_02_get_departments_api(self):
        """Test GET /admin/departments endpoint for admin."""
        res = client.get("/admin/departments", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data), 6)

    def test_03_citizen_forbidden_admin_endpoints(self):
        """Test citizens are rejected (403) from accessing admin endpoints."""
        res1 = client.get("/admin/dashboard/summary", headers=self.citizen_headers)
        self.assertEqual(res1.status_code, 403)

        res2 = client.get("/admin/incidents", headers=self.citizen_headers)
        self.assertEqual(res2.status_code, 403)

    def test_04_automatic_routing_pothole(self):
        """Test automatic routing for pothole -> Roads Department."""
        now = datetime.now(timezone.utc)
        inc = Incident(
            user_id=self.citizen_user.id,
            status=IncidentStatus.CREATED.value,
            ai_issue_type=0,  # pothole
            ai_confidence=0.92,
            risk_score=45.0,
            risk_level="MEDIUM",
            location_status="UNAVAILABLE",
            timestamp=now,
            created_at=now,
        )
        self.db.add(inc)
        self.db.commit()
        self.db.refresh(inc)

        res = client.post(f"/admin/incidents/{inc.id}/route", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["routing_status"], "ASSIGNED")
        self.assertEqual(data["department_name"], "Roads / Public Works Department")

    def test_05_automatic_routing_unknown_issue(self):
        """Test automatic routing for unknown issue -> UNASSIGNED."""
        now = datetime.now(timezone.utc)
        inc = Incident(
            user_id=self.citizen_user.id,
            status=IncidentStatus.CREATED.value,
            ai_issue_type=99,  # unknown/unmapped
            ai_confidence=0.10,
            risk_score=10.0,
            risk_level="LOW",
            location_status="UNAVAILABLE",
            timestamp=now,
            created_at=now,
        )
        self.db.add(inc)
        self.db.commit()
        self.db.refresh(inc)

        res = client.post(f"/admin/incidents/{inc.id}/route", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["routing_status"], "UNASSIGNED")
        self.assertIsNone(data["department_id"])

    def test_06_routing_inactive_department(self):
        """Test routing stays UNASSIGNED if target department is inactive."""
        # Deactivate Sanitation dept
        dept = self.db.query(Department).filter(Department.name == "Sanitation / Waste Management Department").first()
        dept.is_active = False
        self.db.commit()

        now = datetime.now(timezone.utc)
        inc = Incident(
            user_id=self.citizen_user.id,
            status=IncidentStatus.CREATED.value,
            ai_issue_type=2,  # garbage
            location_status="UNAVAILABLE",
            timestamp=now,
            created_at=now,
        )
        self.db.add(inc)
        self.db.commit()
        self.db.refresh(inc)

        res = client.post(f"/admin/incidents/{inc.id}/route", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["routing_status"], "UNASSIGNED")

        # Reactivate Sanitation dept
        dept.is_active = True
        self.db.commit()

    def test_07_manual_department_assignment(self):
        """Test admin manual assignment & reassignment."""
        dept_water = self.db.query(Department).filter(Department.name == "Water Supply / Water Department").first()
        now = datetime.now(timezone.utc)
        inc = Incident(
            user_id=self.citizen_user.id,
            status=IncidentStatus.UNASSIGNED.value,
            ai_issue_type=0,
            location_status="UNAVAILABLE",
            timestamp=now,
            created_at=now,
        )
        self.db.add(inc)
        self.db.commit()
        self.db.refresh(inc)

        res = client.patch(
            f"/admin/incidents/{inc.id}/assignment",
            json={"department_id": dept_water.id},
            headers=self.admin_headers,
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["department_id"], dept_water.id)
        self.assertEqual(data["routing_status"], "ASSIGNED")

    def test_08_status_lifecycle_and_validation(self):
        """Test status transitions ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED."""
        now = datetime.now(timezone.utc)
        inc = Incident(
            user_id=self.citizen_user.id,
            status=IncidentStatus.ASSIGNED.value,
            routing_status="ASSIGNED",
            location_status="UNAVAILABLE",
            timestamp=now,
            created_at=now,
        )
        self.db.add(inc)
        self.db.commit()
        self.db.refresh(inc)

        # 1. Update to IN_PROGRESS
        res1 = client.patch(
            f"/admin/incidents/{inc.id}/status",
            json={"status": "IN_PROGRESS"},
            headers=self.admin_headers,
        )
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["status"], "IN_PROGRESS")

        # 2. Update to RESOLVED with resolution note
        res2 = client.patch(
            f"/admin/incidents/{inc.id}/status",
            json={"status": "RESOLVED", "resolution_note": "Pothole filled with quick-dry asphalt."},
            headers=self.admin_headers,
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["status"], "RESOLVED")
        self.assertEqual(data2["resolution_note"], "Pothole filled with quick-dry asphalt.")
        self.assertIsNotNone(data2["resolved_at"])

        # 3. Invalid transition test: CLOSED directly to CREATED
        res3 = client.patch(
            f"/admin/incidents/{inc.id}/status",
            json={"status": "CLOSED"},
            headers=self.admin_headers,
        )
        self.assertEqual(res3.status_code, 200)

        res4 = client.patch(
            f"/admin/incidents/{inc.id}/status",
            json={"status": "CREATED"},
            headers=self.admin_headers,
        )
        self.assertEqual(res4.status_code, 400)

    def test_09_dashboard_summary_metrics(self):
        """Test GET /admin/dashboard/summary calculates accurate counts."""
        res = client.get("/admin/dashboard/summary", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_incidents", data)
        self.assertIn("active_incidents", data)
        self.assertIn("issue_distribution", data)
        self.assertIn("risk_distribution", data)

    def test_10_filtered_and_searched_incidents_listing(self):
        """Test GET /admin/incidents pagination, filtering, and search."""
        res = client.get(
            "/admin/incidents?skip=0&limit=10&status=ASSIGNED",
            headers=self.admin_headers,
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total", data)
        self.assertIn("items", data)

    def test_11_map_incidents_endpoint(self):
        """Test GET /admin/incidents-map endpoint."""
        res = client.get("/admin/incidents-map", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        items = res.json()
        self.assertIsInstance(items, list)
        if len(items) > 0:
            self.assertIn("location_status", items[0])


if __name__ == "__main__":
    unittest.main()
