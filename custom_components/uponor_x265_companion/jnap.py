"""JNAP client for communicating with Uponor X265 controller."""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientError, ClientSession

_LOGGER = logging.getLogger(__name__)


class JNAPClient:
    """Client for JNAP communication with Uponor X265."""

    def __init__(self, host: str, timeout: int = 10):
        """Initialize the JNAP client."""
        self.host = host
        self.base_url = f"http://{host}/JNAP/"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[ClientSession] = None
        
    async def _ensure_session(self) -> ClientSession:
        """Ensure we have an active session."""
        if self._session is None or self._session.closed:
            self._session = ClientSession(timeout=self.timeout)
        return self._session
        
    async def close(self):
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get_attributes(self, variables: List[str]) -> Optional[Dict[str, Any]]:
        """Get attributes from the controller."""
        headers = {
            "Content-Type": "application/json",
            "x-jnap-action": "http://phyn.com/jnap/uponorsky/GetAttributes",
        }
        
        payload = {}
        if variables:
            payload = {"waspVarNames": variables}
        
        try:
            session = await self._ensure_session()
            async with session.post(
                self.base_url, 
                headers=headers, 
                json=payload
            ) as response:
                if response.status == 200:
                    text = await response.text()
                    try:
                        raw_response = json.loads(text)
                        return self._parse_response(raw_response)
                    except json.JSONDecodeError:
                        _LOGGER.error("Failed to decode JSON response: %s", text)
                        return None
                else:
                    _LOGGER.error(
                        "HTTP error %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return None
                    
        except ClientError as err:
            _LOGGER.error("Connection error: %s", err)
            return None
        except asyncio.TimeoutError:
            _LOGGER.error("Request timed out")
            return None
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            return None
    
    async def set_attribute(self, variable: str, value: Any) -> bool:
        """Set an attribute on the controller."""
        headers = {
            "Content-Type": "application/json",
            "X-JNAP-Action": "SetAttributes",
        }
        
        payload = {
            "waspVarName": variable,
            "waspVarValue": str(value),
        }
        
        try:
            session = await self._ensure_session()
            async with session.post(
                self.base_url,
                headers=headers,
                json=payload
            ) as response:
                return response.status == 200
                
        except Exception as err:
            _LOGGER.error("Failed to set attribute %s: %s", variable, err)
            return False
    
    def _parse_response(self, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the nested JNAP response format into a flat dictionary."""
        # Handle the format: {"result": "OK", "output": {"vars": [{"waspVarName": "...", "waspVarValue": "..."}]}}
        if "output" in raw_response and "vars" in raw_response["output"]:
            parsed_data = {}
            for var_entry in raw_response["output"]["vars"]:
                if "waspVarName" in var_entry and "waspVarValue" in var_entry:
                    parsed_data[var_entry["waspVarName"]] = var_entry["waspVarValue"]
            return parsed_data
        
        # Fallback for other formats or direct variable responses
        return raw_response
    
    async def discover_variables(self) -> List[str]:
        """Discover all available variables from the controller."""
        data = await self.get_attributes([])
        if data:
            return list(data.keys())
        return []