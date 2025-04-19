import requests
from typing import Dict, Any, List
from ...core.config import settings

class ComplianceChecker:
    def __init__(self):
        self.api_key = settings.COMPLYADVANTAGE_API_KEY
        self.base_url = settings.COMPLYADVANTAGE_API_URL
        self.headers = {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/json'
        }

    def check_sanctions(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check customer against sanctions lists.
        
        Args:
            customer_data: Dictionary containing customer information
            
        Returns:
            Dictionary containing sanctions check results
        """
        try:
            # Prepare search parameters
            search_params = {
                'search_term': f"{customer_data['first_name']} {customer_data['last_name']}",
                'fuzziness': 0.6,
                'search_profile': 'sanctions_only',
                'limit': 10
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/searches/",
                headers=self.headers,
                json=search_params
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
            
            results = response.json()
            
            # Process results
            matches = []
            for hit in results.get('hits', []):
                match = {
                    'name': hit.get('name'),
                    'score': hit.get('score'),
                    'source': hit.get('source'),
                    'type': hit.get('type'),
                    'url': hit.get('url')
                }
                matches.append(match)
            
            return {
                'status': 'completed',
                'matches_found': len(matches) > 0,
                'matches': matches,
                'search_id': results.get('search_id'),
                'timestamp': results.get('timestamp')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'matches_found': False,
                'matches': []
            }

    def check_pep(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if customer is a Politically Exposed Person (PEP).
        
        Args:
            customer_data: Dictionary containing customer information
            
        Returns:
            Dictionary containing PEP check results
        """
        try:
            # Prepare search parameters
            search_params = {
                'search_term': f"{customer_data['first_name']} {customer_data['last_name']}",
                'fuzziness': 0.6,
                'search_profile': 'pep_only',
                'limit': 10
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/searches/",
                headers=self.headers,
                json=search_params
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
            
            results = response.json()
            
            # Process results
            matches = []
            for hit in results.get('hits', []):
                match = {
                    'name': hit.get('name'),
                    'score': hit.get('score'),
                    'position': hit.get('position'),
                    'country': hit.get('country'),
                    'url': hit.get('url')
                }
                matches.append(match)
            
            return {
                'status': 'completed',
                'is_pep': len(matches) > 0,
                'matches': matches,
                'search_id': results.get('search_id'),
                'timestamp': results.get('timestamp')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'is_pep': False,
                'matches': []
            }

    def check_adverse_media(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check customer against adverse media databases.
        
        Args:
            customer_data: Dictionary containing customer information
            
        Returns:
            Dictionary containing adverse media check results
        """
        try:
            # Prepare search parameters
            search_params = {
                'search_term': f"{customer_data['first_name']} {customer_data['last_name']}",
                'fuzziness': 0.6,
                'search_profile': 'adverse_media',
                'limit': 10
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/searches/",
                headers=self.headers,
                json=search_params
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
            
            results = response.json()
            
            # Process results
            matches = []
            for hit in results.get('hits', []):
                match = {
                    'title': hit.get('title'),
                    'score': hit.get('score'),
                    'source': hit.get('source'),
                    'date': hit.get('date'),
                    'url': hit.get('url')
                }
                matches.append(match)
            
            return {
                'status': 'completed',
                'matches_found': len(matches) > 0,
                'matches': matches,
                'search_id': results.get('search_id'),
                'timestamp': results.get('timestamp')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'matches_found': False,
                'matches': []
            }

    def perform_all_checks(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform all compliance checks in parallel.
        
        Args:
            customer_data: Dictionary containing customer information
            
        Returns:
            Dictionary containing all compliance check results
        """
        try:
            sanctions_result = self.check_sanctions(customer_data)
            pep_result = self.check_pep(customer_data)
            adverse_media_result = self.check_adverse_media(customer_data)
            
            # Determine overall risk level
            risk_level = 'low'
            if (
                sanctions_result.get('matches_found', False) or
                pep_result.get('is_pep', False) or
                adverse_media_result.get('matches_found', False)
            ):
                risk_level = 'high'
            
            return {
                'status': 'completed',
                'risk_level': risk_level,
                'sanctions_check': sanctions_result,
                'pep_check': pep_result,
                'adverse_media_check': adverse_media_result
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'risk_level': 'unknown',
                'sanctions_check': {'status': 'error'},
                'pep_check': {'status': 'error'},
                'adverse_media_check': {'status': 'error'}
            } 