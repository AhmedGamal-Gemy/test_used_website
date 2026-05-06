"""
Pydantic models for part CRUD operations (create, read, update, delete).

For junior developers:
- These Pydantic models define the shape of request bodies and response data
- PartCreate: what a client sends when creating a new part listing
- PartUpdate: what a client sends when updating an existing part (all fields optional)
- PartResponse: what our API sends back to clients (includes system-generated fields like id, seller_id, timestamps)
- Using BaseModel from Pydantic gives us automatic validation and OpenAPI documentation
"""

from pydantic import BaseModel


# ------------------------------------------------------------------------------
# Request Schemas (what clients send to our API)
# ------------------------------------------------------------------------------

class PartCreate(BaseModel):
    """
    Schema for creating a new part listing.

    This is the data a client sends when they want to list a computer part for sale.
    Required fields: title, category, compatible_models, condition, price
    Optional field: description (defaults to empty string if not provided)

    For junior developers:
    - price is a float to allow decimal values (e.g., 299.99)
    - condition could be "new", "like new", "good", "fair", etc. (validated at application level)
    - compatible_models is a list of strings representing laptop/device models this part works with
    - description has a default value of "" so clients don't have to provide it
    """
    title: str
    category: str
    compatible_models: list[str]
    condition: str
    price: float
    description: str = ""


class PartUpdate(BaseModel):
    """
    Schema for updating an existing part listing.

    All fields are optional - clients only need to send the fields they want to change.
    Fields not included in the request will keep their current values in the database.

    For junior developers:
    - This uses Optional types with None defaults
    - FastAPI/Pydantic will only validate fields that are actually provided in the request
    - The API will only update the fields that are present in the request body
    """
    title: str | None = None
    category: str | None = None
    compatible_models: list[str] | None = None
    condition: str | None = None
    price: float | None = None
    description: str | None = None


# ------------------------------------------------------------------------------
# Response Schema (what our API sends back to clients)
# ------------------------------------------------------------------------------

class PartResponse(BaseModel):
    """
    Schema for part data returned to clients.

    This includes all the fields from PartCreate plus system-generated fields:
    - id: the MongoDB _id converted to string
    - image_url: optional URL to the part's image (uploaded separately in Task 7)
    - seller_id: the ID of the user who listed this part
    - created_at: when the listing was created
    - updated_at: when the listing was last updated

    For junior developers:
    - image_url is Optional (can be None) because images are uploaded separately
    - seller_id is a string (converted from MongoDB's ObjectId)
    - created_at and updated_at are typically datetime objects or ISO format strings
    - compatible_models is a list of strings
    """
    id: str
    title: str
    category: str
    compatible_models: list[str]
    condition: str
    price: float
    description: str
    image_url: str | None = None
    seller_id: str
    created_at: str  # ISO format datetime string
    updated_at: str  # ISO format datetime string
