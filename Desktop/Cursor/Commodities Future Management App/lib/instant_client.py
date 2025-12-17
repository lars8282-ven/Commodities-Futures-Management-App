"""
InstantDB client for Python/Streamlit app.
Uses Next.js API routes as a bridge to InstantDB.
"""
import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class InstantDBClient:
    """Client for interacting with InstantDB via Next.js API routes."""
    
    def __init__(self, api_base_url: Optional[str] = None):
        """
        Initialize the InstantDB client.
        
        Args:
            api_base_url: Base URL for Next.js API (defaults to localhost:3000)
        """
        self.api_base_url = api_base_url or os.getenv(
            "NEXTJS_API_URL", 
            "http://localhost:3000/api"
        )
        self.app_id = os.getenv("NEXT_PUBLIC_INSTANT_APP_ID") or os.getenv("INSTANT_APP_ID")
        
        if not self.app_id:
            print("Warning: INSTANT_APP_ID not set. API calls may fail.")
    
    def query(self, entity: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query entities from InstantDB via API route.
        
        Args:
            entity: Entity name (e.g., 'futuresContracts', 'spotPrices', 'errorCalculations')
            filters: Optional filters dictionary
            
        Returns:
            List of entity records
        """
        # Map entity names to API routes
        route_map = {
            "futuresContracts": "futures",
            "spotPrices": "spot",
            "errorCalculations": "errors",
            "scrapeLogs": "scrapelogs",
        }
        
        route = route_map.get(entity, entity.lower())
        url = f"{self.api_base_url}/{route}"
        
        # Convert filters to query parameters
        params = {}
        if filters:
            for key, value in filters.items():
                if isinstance(value, dict):
                    # Handle operators like $gte, $lte
                    for op, op_value in value.items():
                        if op == "$gte":
                            params[f"{key}_start"] = op_value
                        elif op == "$lte":
                            params[f"{key}_end"] = op_value
                else:
                    params[key] = value
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"Error querying {entity}: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return []
    
    def insert(self, entity: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Insert a new record into InstantDB via API route.
        
        Args:
            entity: Entity name
            data: Record data dictionary
            
        Returns:
            Created record or None if failed
        """
        route_map = {
            "futuresContracts": "futures",
            "spotPrices": "spot",
            "errorCalculations": "errors",
            "scrapeLogs": "scrapelogs",
        }
        
        route = route_map.get(entity, entity.lower())
        url = f"{self.api_base_url}/{route}"
        
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get("data")
        except requests.exceptions.RequestException as e:
            print(f"Error inserting into {entity}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response: {e.response.text}")
            return None
    
    def bulk_insert(self, entity: str, records: List[Dict[str, Any]]) -> int:
        """
        Insert multiple records into InstantDB.
        
        Args:
            entity: Entity name
            records: List of record dictionaries
            
        Returns:
            Number of successfully inserted records
        """
        success_count = 0
        for record in records:
            result = self.insert(entity, record)
            if result:
                success_count += 1
        return success_count
    
    def update(self, entity: str, record_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing record in InstantDB.
        Note: InstantDB uses transactions, so we'll need to query first then update.
        
        Args:
            entity: Entity name
            record_id: Record ID to update
            data: Updated data dictionary
            
        Returns:
            Updated record or None if failed
        """
        # For now, we'll use insert which will update if ID exists
        # This is a limitation - ideally we'd have a PATCH endpoint
        data_with_id = {**data, "id": record_id}
        return self.insert(entity, data_with_id)
    
    def delete(self, entity: str, record_id: str) -> bool:
        """
        Delete a record from InstantDB.
        Note: This requires a DELETE endpoint in the API routes.
        
        Args:
            entity: Entity name
            record_id: Record ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        route_map = {
            "futuresContracts": "futures",
            "spotPrices": "spot",
            "errorCalculations": "errors",
            "scrapeLogs": "scrapelogs",
        }
        
        route = route_map.get(entity, entity.lower())
        url = f"{self.api_base_url}/{route}/{record_id}"
        
        try:
            response = requests.delete(url, timeout=30)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting {entity}/{record_id}: {e}")
            return False


# Global client instance
_db_client: Optional[InstantDBClient] = None

def get_db() -> InstantDBClient:
    """Get or create the global InstantDB client instance."""
    global _db_client
    if _db_client is None:
        _db_client = InstantDBClient()
    return _db_client
