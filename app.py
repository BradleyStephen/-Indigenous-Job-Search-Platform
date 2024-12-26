from flask import Flask, render_template, request, flash, redirect, url_for
from google.cloud import talent_v4beta1
from indigenous_job_platform import IndigenousJobPlatform
import os

app = Flask(__name__)
app.secret_key = '' 

# Initialize the job platform
project_id = "your-project-id"  # Replace with your Google Cloud project ID
platform = IndigenousJobPlatform(project_id)

@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')

@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    """Handle job posting form."""
    if request.method == 'POST':
        try:
            job_details = {
                'title': request.form['title'],
                'description': request.form['description'],
                'addresses': [request.form['location']],
                'benefits': [
                    talent_v4beta1.Job.JobBenefit.PAID_TIME_OFF,
                    talent_v4beta1.Job.JobBenefit.HEALTH_INSURANCE
                ] if request.form.get('benefits') else [],
                'custom_attributes': {
                    'indigenous_focused': {
                        'string_values': ['true'],
                        'filterable': True
                    }
                }
            }
            
            platform.create_job(job_details)
            flash('Job posted successfully!', 'success')
            return redirect(url_for('home'))
            
        except Exception as e:
            flash(f'Error posting job: {str(e)}', 'error')
    
    return render_template('post_job.html')

@app.route('/search', methods=['GET', 'POST'])
def search_jobs():
    """Handle job search."""
    jobs = []
    if request.method == 'POST':
        try:
            query = request.form['query']
            location = request.form.get('location', '')
            jobs = platform.search_jobs(query, location)
            
        except Exception as e:
            flash(f'Error searching jobs: {str(e)}', 'error')
    
    return render_template('search.html', jobs=jobs)

if __name__ == '__main__':
    # Ensure tenant and company are created
    platform.create_tenant("indigenous-job-platform")
    platform.create_company(
        company_name="Indigenous Development Corp",
        external_id="idc-001"
    )
    
    app.run(debug=True)
