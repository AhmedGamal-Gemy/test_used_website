"""
Pydantic models for laptop CRUD operations (create, read, update, delete).

For junior developers:
- These Pydantic models define the shape of request bodies and response data
- LaptopCreate: what a client sends when creating a new laptop listing
- LaptopUpdate: what a client sends when updating an existing laptop (all fields optional)
- LaptopResponse: what our API sends back to clients (includes system-generated fields like id, seller_id, timestamps)
- Using BaseModel from Pydantic gives us automatic validation and OpenAPI documentation
"""

from pydantic import BaseModel


# ------------------------------------------------------------------------------
# Request Schemas (what clients send to our API)
# ------------------------------------------------------------------------------

class LaptopCreate(BaseModel):
    """
    Schema for creating a new laptop listing.

    This is the data a client sends when they want to list a laptop for sale.
    Required fields: title, brand, model, condition, price
    Optional field: description (defaults to empty string if not provided)

    For junior developers:
    - price is a float to allow decimal values (e.g., 599.99)
    - condition could be "new", "like new", "good", "fair", etc. (validated at application level)
    - description has a default value of "" so clients don't have to provide it
    """
    title: str
    brand: str
    model: str
    condition: str
    price: float
    description: str = ""


class LaptopUpdate(BaseModel):
    """
    Schema for updating an existing laptop listing.

    All fields are optional - clients only need to send the fields they want to change.
    Fields not included in the request will keep their current values in the database.

    For junior developers:
    - This uses Optional types with None defaults
    - FastAPI/Pydantic will only validate fields that are actually provided in the request
    - The API will only update the fields that are present in the request body
    """
    title: str | None = None
    brand: str | None = None
    model: str | None = None
    condition: str | None = None
    price: float | None = None
    description: str | None = None


# ------------------------------------------------------------------------------
# Response Schema (what our API sends back to clients)
# ------------------------------------------------------------------------------

class LaptopResponse(BaseModel):
    """
    Schema for laptop data returned to clients.

    This includes all the fields from LaptopCreate plus system-generated fields:
    - id: the MongoDB _id converted to string
    - image_url: optional URL to the laptop's image (uploaded separately in Task 7)
    - seller_id: the ID of the user who listed this laptop
    - created_at: when the listing was created
    - updated_at: when the listing was last updated

    For junior developers:
    - image_url is Optional (can be None) because images are uploaded separately
    - seller_id is a string (converted from MongoDB's ObjectId)
    - created_at and updated_at are typically datetime objects or ISO format strings
    """
    id: str
    title: str
    brand: str
    model: str
    condition: str
    price: float
    description: str
    image_url: str | None = None
    seller_id: str
    created_at: str  # ISO format datetime string
    updated_at: str  # ISO format datetime string
