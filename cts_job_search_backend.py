from google.cloud import talent_v4beta1
from google.cloud.talent_v4beta1 import (
    Company,
    Job,
    CreateTenantRequest,
    CreateCompanyRequest,
    CreateJobRequest,
    SearchJobsRequest,
    JobQuery,
)
from google.cloud.talent_v4beta1.services.tenant_service import TenantServiceClient
from google.cloud.talent_v4beta1.services.company_service import CompanyServiceClient
from google.cloud.talent_v4beta1.services.job_service import JobServiceClient
from google.api_core import retry
import os

class IndigenousJobPlatform:
    def __init__(self, project_id):
        """
        Initialize the job platform with Google Cloud project credentials.
        
        Args:
            project_id (str): Google Cloud project ID
        """
        self.project_id = project_id
        self.project_path = f"projects/{project_id}"
        
        # Initialize clients
        self.tenant_client = TenantServiceClient()
        self.company_client = CompanyServiceClient()
        self.job_client = JobServiceClient()
        
        # Store tenant and company details
        self.tenant_path = None
        self.company_path = None

    def create_tenant(self, external_id):
        """
        Create a new tenant for the job platform.
        
        Args:
            external_id (str): External identifier for the tenant
            
        Returns:
            str: Created tenant path
        """
        try:
            tenant = talent_v4beta1.Tenant(
                external_id=external_id,
            )
            
            request = CreateTenantRequest(
                parent=self.project_path,
                tenant=tenant,
            )
            
            created_tenant = self.tenant_client.create_tenant(request=request)
            self.tenant_path = created_tenant.name
            print(f"Created tenant: {self.tenant_path}")
            return self.tenant_path
            
        except Exception as e:
            print(f"Error creating tenant: {str(e)}")
            raise

    def create_company(self, company_name, external_id):
        """
        Create a new company within the tenant.
        
        Args:
            company_name (str): Name of the company
            external_id (str): External identifier for the company
            
        Returns:
            str: Created company path
        """
        try:
            company = Company(
                display_name=company_name,
                external_id=external_id,
            )
            
            request = CreateCompanyRequest(
                parent=self.tenant_path,
                company=company,
            )
            
            created_company = self.company_client.create_company(request=request)
            self.company_path = created_company.name
            print(f"Created company: {self.company_path}")
            return self.company_path
            
        except Exception as e:
            print(f"Error creating company: {str(e)}")
            raise

    def create_job(self, job_details):
        """
        Create a new job posting.
        
        Args:
            job_details (dict): Dictionary containing job details
            
        Returns:
            Job: Created job object
        """
        try:
            job = Job(
                company=self.company_path,
                title=job_details['title'],
                description=job_details['description'],
                language_code=job_details.get('language_code', 'en-US'),
                job_benefits=job_details.get('benefits', []),
                posting_region=job_details.get('posting_region', Job.PostingRegion.NATION),
                addresses=job_details.get('addresses', []),
                application_info=job_details.get('application_info', {}),
                custom_attributes=job_details.get('custom_attributes', {}),
            )
            
            request = CreateJobRequest(
                parent=self.tenant_path,
                job=job,
            )
            
            created_job = self.job_client.create_job(request=request)
            print(f"Created job: {created_job.name}")
            return created_job
            
        except Exception as e:
            print(f"Error creating job: {str(e)}")
            raise

    def search_jobs(self, query_string, location=None):
        """
        Search for jobs based on query string and optional location.
        
        Args:
            query_string (str): Search query
            location (str, optional): Location filter
            
        Returns:
            list: List of matching jobs
        """
        try:
            job_query = JobQuery(
                query=query_string,
                location_filters=location if location else None,
            )
            
            request = SearchJobsRequest(
                parent=self.tenant_path,
                job_query=job_query,
                search_mode=SearchJobsRequest.SearchMode.JOB_SEARCH,
            )
            
            search_response = self.job_client.search_jobs(request=request)
            
            matching_jobs = []
            for result in search_response.matching_jobs:
                job = result.job
                matching_jobs.append({
                    'title': job.title,
                    'company': job.company,
                    'description': job.description,
                    'location': job.addresses[0] if job.addresses else None,
                })
            
            return matching_jobs
            
        except Exception as e:
            print(f"Error searching jobs: {str(e)}")
            raise

def main():
    """
    Example usage of the IndigenousJobPlatform class.
    """
    # Set your Google Cloud project ID
    project_id = "your-project-id"
    
    # Initialize the platform
    platform = IndigenousJobPlatform(project_id)
    
    # Create a tenant
    platform.create_tenant("indigenous-job-platform")
    
    # Create a company
    platform.create_company(
        company_name="Indigenous Development Corp",
        external_id="idc-001"
    )
    
    # Create sample job postings
    sample_jobs = [
        {
            'title': 'Indigenous Community Liaison',
            'description': 'Working with Indigenous communities to develop economic opportunities.',
            'addresses': ['Vancouver, BC, Canada'],
            'benefits': [
                Job.JobBenefit.PAID_TIME_OFF,
                Job.JobBenefit.HEALTH_INSURANCE,
            ],
            'custom_attributes': {
                'indigenous_focused': {'string_values': ['true'], 'filterable': True},
            }
        },
        {
            'title': 'Cultural Program Manager',
            'description': 'Managing cultural preservation and education programs.',
            'addresses': ['Toronto, ON, Canada'],
            'benefits': [
                Job.JobBenefit.PAID_TIME_OFF,
                Job.JobBenefit.HEALTH_INSURANCE,
            ],
            'custom_attributes': {
                'indigenous_focused': {'string_values': ['true'], 'filterable': True},
            }
        }
    ]
    
    for job in sample_jobs:
        platform.create_job(job)
    
    # Search for jobs
    results = platform.search_jobs("Indigenous", "Canada")
    
    # Print results
    for job in results:
        print(f"\nFound job: {job['title']}")
        print(f"Location: {job['location']}")
        print(f"Description: {job['description']}")

if __name__ == "__main__":
    main()
