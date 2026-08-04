from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from flowlens.schemas import OrganizationCreate, OrganizationResponse


def test_accepts_valid_organization_input() -> None:
    organization = OrganizationCreate(
        name="Northstar Business Services",
        slug="northstar-business-services",
    )

    assert organization.name == "Northstar Business Services"
    assert organization.slug == "northstar-business-services"


@pytest.mark.parametrize(
    "invalid_slug",
    [
        "Northstar",
        "northstar business services",
        "northstar_business_services",
        "-northstar",
        "northstar-",
    ],
)
def test_rejects_invalid_organization_slugs(
    invalid_slug: str,
) -> None:
    with pytest.raises(ValidationError):
        OrganizationCreate(
            name="Northstar Business Services",
            slug=invalid_slug,
        )


def test_builds_organization_response() -> None:
    now = datetime.now(UTC)

    response = OrganizationResponse(
        id=uuid4(),
        name="Northstar Business Services",
        slug="northstar-business-services",
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    assert response.name == "Northstar Business Services"
    assert response.is_active is True