


import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from database import get_db_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

@app.route('/')
def dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute('SELECT COUNT(*) AS total FROM companies')
    companies = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM jobs')
    jobs = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM applications')
    applications = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM contacts')
    contacts = cursor.fetchone()['total']

    cursor.close()
    connection.close()


    return render_template(
        'dashboard.html',
        companies=companies,
        jobs=jobs,
        applications=applications,
        contacts=contacts
    )




  

@app.route('/companies')
def companies():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT company_id, company_name, industry,
               website, city, state
        FROM companies
        ORDER BY company_name
    """)

    company_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'companies.html',
        companies=company_list
    )








@app.route('/companies/add', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        industry = request.form.get('industry', '').strip()
        website = request.form.get('website', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()

        if not company_name:
            flash('Company name is required.', 'danger')
            return render_template('company_form.html',
                                   company=request.form, action='Add')

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO companies
                (company_name, industry, website, city, state)
                VALUES (%s, %s, %s, %s, %s)
            """, (company_name, industry or None,
                  website or None, city or None, state or None))

            connection.commit()
            flash('Company added successfully!', 'success')
            return redirect(url_for('companies'))

        except Exception:
            connection.rollback()
            flash('Unable to add company.', 'danger')

        finally:
            cursor.close()
            connection.close()

    return render_template('company_form.html',
                           company=None, action='Add')










@app.route('/companies/edit/<int:company_id>', methods=['GET', 'POST'])
def edit_company(company_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM companies WHERE company_id = %s",
            (company_id,)
        )
        company = cursor.fetchone()

        if not company:
            flash('Company not found.', 'danger')
            return redirect(url_for('companies'))

        if request.method == 'POST':
            company_name = request.form.get('company_name', '').strip()
            industry = request.form.get('industry', '').strip()
            website = request.form.get('website', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()

            if not company_name:
                flash('Company name is required.', 'danger')
                return render_template(
                    'company_form.html',
                    company=request.form,
                    action='Edit'
                )

            cursor.execute("""
                UPDATE companies
                SET company_name = %s,
                    industry = %s,
                    website = %s,
                    city = %s,
                    state = %s
                WHERE company_id = %s
            """, (
                company_name, industry or None,
                website or None, city or None,
                state or None, company_id
            ))

            connection.commit()
            flash('Company updated successfully!', 'success')
            return redirect(url_for('companies'))

        return render_template(
            'company_form.html',
            company=company,
            action='Edit'
        )

    except Exception:
        connection.rollback()
        flash('Unable to update company.', 'danger')
        return redirect(url_for('companies'))

    finally:
        cursor.close()
        connection.close()


@app.route('/companies/delete/<int:company_id>', methods=['POST'])
def delete_company(company_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM companies WHERE company_id = %s",
            (company_id,)
        )
        connection.commit()

        if cursor.rowcount:
            flash('Company deleted successfully!', 'success')
        else:
            flash('Company not found.', 'warning')

    except Exception:
        connection.rollback()
        flash(
            'Unable to delete company. It may have related jobs or contacts.',
            'danger'
        )

    finally:
        cursor.close()
        connection.close()






    return redirect(url_for('companies'))










@app.route('/jobs')
def jobs():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            j.job_id,
            j.company_id,
            j.job_title,
            j.job_description,
            j.salary_min,
            j.salary_max,
            j.job_type,
            j.posting_url,
            j.date_posted,
            j.is_active,
            j.requirements,
            c.company_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY j.job_id DESC
    """)

    job_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'jobs.html',
        jobs=job_list
    )










@app.route('/jobs/add', methods=['GET', 'POST'])
def add_job():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT company_id, company_name
            FROM companies
            ORDER BY company_name
        """)
        company_list = cursor.fetchall()

        if request.method == 'POST':
            company_id = request.form.get('company_id')
            job_title = request.form.get('job_title', '').strip()
            job_description = request.form.get('job_description', '').strip()
            salary_min = request.form.get('salary_min') or None
            salary_max = request.form.get('salary_max') or None
            job_type = request.form.get('job_type', '').strip()
            posting_url = request.form.get('posting_url', '').strip()
            date_posted = request.form.get('date_posted') or None
            is_active = 1 if request.form.get('is_active') else 0
            requirements_text = request.form.get('requirements', '').strip()

            if not company_id or not job_title:
                flash('Company and job title are required.', 'danger')
                return render_template(
                    'job_form.html',
                    companies=company_list,
                    job=request.form,
                    action='Add'
                )

            requirements_json = None

            if requirements_text:
                try:
                    requirements_json = json.dumps(
                        json.loads(requirements_text)
                    )
                except json.JSONDecodeError:
                    flash('Requirements must contain valid JSON.', 'danger')
                    return render_template(
                        'job_form.html',
                        companies=company_list,
                        job=request.form,
                        action='Add'
                    )

            cursor.execute("""
                INSERT INTO jobs
                (
                    company_id, job_title, job_description,
                    salary_min, salary_max, job_type,
                    posting_url, date_posted, is_active,
                    requirements
                )
                VALUES (%s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s)
            """, (
                company_id, job_title,
                job_description or None,
                salary_min, salary_max,
                job_type or None,
                posting_url or None,
                date_posted, is_active,
                requirements_json
            ))

            connection.commit()
            flash('Job added successfully!', 'success')
            return redirect(url_for('jobs'))

        return render_template(
            'job_form.html',
            companies=company_list,
            job=None,
            action='Add'
        )

    except Exception:
        connection.rollback()
        flash('Unable to add job.', 'danger')
        return redirect(url_for('jobs'))

    finally:
        cursor.close()
        connection.close()






@app.route('/jobs/edit/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT company_id, company_name
            FROM companies
            ORDER BY company_name
        """)
        company_list = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM jobs WHERE job_id = %s",
            (job_id,)
        )
        job = cursor.fetchone()

        if not job:
            flash('Job not found.', 'danger')
            return redirect(url_for('jobs'))

        if request.method == 'POST':
            company_id = request.form.get('company_id')
            job_title = request.form.get('job_title', '').strip()
            job_description = request.form.get('job_description', '').strip()
            salary_min = request.form.get('salary_min') or None
            salary_max = request.form.get('salary_max') or None
            job_type = request.form.get('job_type', '').strip()
            posting_url = request.form.get('posting_url', '').strip()
            date_posted = request.form.get('date_posted') or None
            is_active = 1 if request.form.get('is_active') else 0
            requirements_text = request.form.get('requirements', '').strip()

            if not company_id or not job_title:
                flash('Company and job title are required.', 'danger')
                return render_template(
                    'job_form.html',
                    companies=company_list,
                    job=request.form,
                    action='Edit'
                )

            requirements_json = None

            if requirements_text:
                try:
                    requirements_json = json.dumps(
                        json.loads(requirements_text)
                    )
                except json.JSONDecodeError:
                    flash('Requirements must contain valid JSON.', 'danger')
                    return render_template(
                        'job_form.html',
                        companies=company_list,
                        job=request.form,
                        action='Edit'
                    )

            cursor.execute("""
                UPDATE jobs
                SET company_id = %s,
                    job_title = %s,
                    job_description = %s,
                    salary_min = %s,
                    salary_max = %s,
                    job_type = %s,
                    posting_url = %s,
                    date_posted = %s,
                    is_active = %s,
                    requirements = %s
                WHERE job_id = %s
            """, (
                company_id,
                job_title,
                job_description or None,
                salary_min,
                salary_max,
                job_type or None,
                posting_url or None,
                date_posted,
                is_active,
                requirements_json,
                job_id
            ))

            connection.commit()
            flash('Job updated successfully!', 'success')
            return redirect(url_for('jobs'))

        if job.get('date_posted'):
            job['date_posted'] = job['date_posted'].isoformat()

        if isinstance(job.get('requirements'), (dict, list)):
            job['requirements'] = json.dumps(job['requirements'])

        return render_template(
            'job_form.html',
            companies=company_list,
            job=job,
            action='Edit'
        )

    except Exception:
        connection.rollback()
        flash('Unable to update job.', 'danger')
        return redirect(url_for('jobs'))

    finally:
        cursor.close()
        connection.close()










@app.route('/jobs/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM jobs WHERE job_id = %s",
            (job_id,)
        )
        deleted_count = cursor.rowcount
        connection.commit()

        if deleted_count:
            flash('Job deleted successfully!', 'success')
        else:
            flash('Job not found.', 'warning')

    except Exception:
        connection.rollback()
        flash(
            'Unable to delete job. It may have related applications.',
            'danger'
        )

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('jobs'))





@app.route('/applications')
def applications():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                a.application_id,
                a.job_id,
                a.application_date,
                a.status,
                a.resume_version,
                a.cover_letter_sent,
                a.response_date,
                a.interview_date,
                a.notes,
                a.interview_data,
                j.job_title,
                c.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies c ON j.company_id = c.company_id
            ORDER BY a.application_date DESC, a.application_id DESC
        """)

        application_list = cursor.fetchall()

        return render_template(
            'applications.html',
            applications=application_list
        )

    finally:
        cursor.close()
        connection.close()





@app.route('/applications/add', methods=['GET', 'POST'])
def add_application():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT j.job_id, j.job_title, c.company_name
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            ORDER BY c.company_name, j.job_title
        """)
        job_list = cursor.fetchall()

        if request.method == 'POST':
            job_id = request.form.get('job_id')
            application_date = request.form.get('application_date')
            status = request.form.get('status', 'Applied')
            resume_version = request.form.get('resume_version', '').strip()
            cover_letter_sent = 1 if request.form.get('cover_letter_sent') else 0
            response_date = request.form.get('response_date') or None
            interview_date = request.form.get('interview_date') or None
            notes = request.form.get('notes', '').strip()

            if not job_id or not application_date:
                flash('Job and application date are required.', 'danger')
                return render_template(
                    'application_form.html',
                    jobs=job_list,
                    application=request.form,
                    action='Add'
                )

            cursor.execute("""
                INSERT INTO applications
                (
                    job_id, application_date, status,
                    resume_version, cover_letter_sent,
                    response_date, interview_date, notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                job_id,
                application_date,
                status,
                resume_version or None,
                cover_letter_sent,
                response_date,
                interview_date,
                notes or None
            ))

            connection.commit()
            flash('Application added successfully!', 'success')
            return redirect(url_for('applications'))

        return render_template(
            'application_form.html',
            jobs=job_list,
            application=None,
            action='Add'
        )

    except Exception:
        connection.rollback()
        flash('Unable to add application.', 'danger')
        return redirect(url_for('applications'))

    finally:
        cursor.close()
        connection.close()







@app.route('/applications/edit/<int:application_id>', methods=['GET', 'POST'])
def edit_application(application_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT j.job_id, j.job_title, c.company_name
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            ORDER BY c.company_name, j.job_title
        """)
        job_list = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM applications WHERE application_id = %s",
            (application_id,)
        )
        application = cursor.fetchone()

        if not application:
            flash('Application not found.', 'danger')
            return redirect(url_for('applications'))

        if request.method == 'POST':
            job_id = request.form.get('job_id')
            application_date = request.form.get('application_date')
            status = request.form.get('status', 'Applied')
            resume_version = request.form.get('resume_version', '').strip()
            cover_letter_sent = 1 if request.form.get('cover_letter_sent') else 0
            response_date = request.form.get('response_date') or None
            interview_date = request.form.get('interview_date') or None
            notes = request.form.get('notes', '').strip()

            if not job_id or not application_date:
                flash('Job and application date are required.', 'danger')
                return render_template(
                    'application_form.html',
                    jobs=job_list,
                    application=request.form,
                    action='Edit'
                )

            cursor.execute("""
                UPDATE applications
                SET job_id = %s,
                    application_date = %s,
                    status = %s,
                    resume_version = %s,
                    cover_letter_sent = %s,
                    response_date = %s,
                    interview_date = %s,
                    notes = %s
                WHERE application_id = %s
            """, (
                job_id,
                application_date,
                status,
                resume_version or None,
                cover_letter_sent,
                response_date,
                interview_date,
                notes or None,
                application_id
            ))

            connection.commit()
            flash('Application updated successfully!', 'success')
            return redirect(url_for('applications'))

        if application.get('application_date'):
            application['application_date'] = (
                application['application_date'].isoformat()
            )

        if application.get('response_date'):
            application['response_date'] = (
                application['response_date'].isoformat()
            )

        if application.get('interview_date'):
            application['interview_date'] = (
                application['interview_date'].strftime('%Y-%m-%dT%H:%M')
            )

        return render_template(
            'application_form.html',
            jobs=job_list,
            application=application,
            action='Edit'
        )

    except Exception:
        connection.rollback()
        flash('Unable to update application.', 'danger')
        return redirect(url_for('applications'))

    finally:
        cursor.close()
        connection.close()








@app.route('/applications/delete/<int:application_id>', methods=['POST'])
def delete_application(application_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM applications WHERE application_id = %s",
            (application_id,)
        )
        deleted_count = cursor.rowcount
        connection.commit()

        if deleted_count:
            flash('Application deleted successfully!', 'success')
        else:
            flash('Application not found.', 'warning')

    except Exception:
        connection.rollback()
        flash('Unable to delete application.', 'danger')

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('applications'))










@app.route('/contacts')
def contacts():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                ct.contact_id,
                ct.company_id,
                ct.first_name,
                ct.last_name,
                ct.email,
                ct.phone,
                ct.job_title,
                ct.linkedin_url,
                ct.notes,
                c.company_name
            FROM contacts ct
            JOIN companies c
                ON ct.company_id = c.company_id
            ORDER BY ct.last_name, ct.first_name
        """)

        contact_list = cursor.fetchall()

        return render_template(
            'contacts.html',
            contacts=contact_list
        )

    finally:
        cursor.close()
        connection.close()





@app.route('/contacts/add', methods=['GET', 'POST'])
def add_contact():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT company_id, company_name
            FROM companies
            ORDER BY company_name
        """)
        company_list = cursor.fetchall()

        if request.method == 'POST':
            company_id = request.form.get('company_id')
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            job_title = request.form.get('job_title', '').strip()
            linkedin_url = request.form.get('linkedin_url', '').strip()
            notes = request.form.get('notes', '').strip()

            if not company_id or not first_name or not last_name:
                flash('Company, first name, and last name are required.', 'danger')
                return render_template(
                    'contact_form.html',
                    companies=company_list,
                    contact=request.form,
                    action='Add'
                )

            cursor.execute("""
                INSERT INTO contacts
                (
                    company_id, first_name, last_name,
                    email, phone, job_title, linkedin_url, notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                company_id,
                first_name,
                last_name,
                email or None,
                phone or None,
                job_title or None,
                linkedin_url or None,
                notes or None
            ))

            connection.commit()
            flash('Contact added successfully!', 'success')
            return redirect(url_for('contacts'))

        return render_template(
            'contact_form.html',
            companies=company_list,
            contact=None,
            action='Add'
        )

    except Exception:
        connection.rollback()
        flash('Unable to add contact.', 'danger')
        return redirect(url_for('contacts'))

    finally:
        cursor.close()
        connection.close()








@app.route('/contacts/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT company_id, company_name
            FROM companies
            ORDER BY company_name
        """)
        company_list = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM contacts WHERE contact_id = %s",
            (contact_id,)
        )
        contact = cursor.fetchone()

        if not contact:
            flash('Contact not found.', 'danger')
            return redirect(url_for('contacts'))

        if request.method == 'POST':
            company_id = request.form.get('company_id')
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            job_title = request.form.get('job_title', '').strip()
            linkedin_url = request.form.get('linkedin_url', '').strip()
            notes = request.form.get('notes', '').strip()

            if not company_id or not first_name or not last_name:
                flash(
                    'Company, first name, and last name are required.',
                    'danger'
                )
                return render_template(
                    'contact_form.html',
                    companies=company_list,
                    contact=request.form,
                    action='Edit'
                )

            cursor.execute("""
                UPDATE contacts
                SET company_id = %s,
                    first_name = %s,
                    last_name = %s,
                    email = %s,
                    phone = %s,
                    job_title = %s,
                    linkedin_url = %s,
                    notes = %s
                WHERE contact_id = %s
            """, (
                company_id,
                first_name,
                last_name,
                email or None,
                phone or None,
                job_title or None,
                linkedin_url or None,
                notes or None,
                contact_id
            ))

            connection.commit()
            flash('Contact updated successfully!', 'success')
            return redirect(url_for('contacts'))

        return render_template(
            'contact_form.html',
            companies=company_list,
            contact=contact,
            action='Edit'
        )

    except Exception:
        connection.rollback()
        flash('Unable to update contact.', 'danger')
        return redirect(url_for('contacts'))

    finally:
        cursor.close()
        connection.close()


@app.route('/contacts/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM contacts WHERE contact_id = %s",
            (contact_id,)
        )
        deleted_count = cursor.rowcount
        connection.commit()

        if deleted_count:
            flash('Contact deleted successfully!', 'success')
        else:
            flash('Contact not found.', 'warning')

    except Exception:
        connection.rollback()
        flash('Unable to delete contact.', 'danger')

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('contacts'))




@app.route('/job-match', methods=['GET', 'POST'])
def job_match():
    matches = []
    user_skills_text = ''
    searched = False

    if request.method == 'POST':
        searched = True
        user_skills_text = request.form.get(
            'skills', ''
        ).strip()

        user_skills = {
            skill.strip().casefold()
            for skill in user_skills_text.split(',')
            if skill.strip()
        }

        if not user_skills:
            flash('Please enter at least one skill.', 'warning')
            return render_template(
                'job_match.html',
                matches=[],
                user_skills_text=user_skills_text,
                searched=False
            )

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    j.job_id,
                    j.job_title,
                    j.requirements,
                    c.company_name
                FROM jobs j
                JOIN companies c
                    ON j.company_id = c.company_id
                WHERE j.requirements IS NOT NULL
                ORDER BY j.job_title
            """)

            job_list = cursor.fetchall()

            for job in job_list:
                requirements = job['requirements']

                if isinstance(requirements, str):
                    try:
                        requirements = json.loads(requirements)
                    except json.JSONDecodeError:
                        continue

                if not isinstance(requirements, dict):
                    continue

                required_skills = requirements.get(
                    'required_skills', []
                )

                if not isinstance(required_skills, list):
                    continue

                required_skills = [
                    skill.strip()
                    for skill in required_skills
                    if isinstance(skill, str) and skill.strip()
                ]

                if not required_skills:
                    continue

                matched_skills = [
                    skill for skill in required_skills
                    if skill.casefold() in user_skills
                ]

                missing_skills = [
                    skill for skill in required_skills
                    if skill.casefold() not in user_skills
                ]

                match_percentage = round(
                    len(matched_skills) /
                    len(required_skills) * 100
                )

                matches.append({
                    'job_title': job['job_title'],
                    'company_name': job['company_name'],
                    'match_percentage': match_percentage,
                    'matched_skills': matched_skills,
                    'missing_skills': missing_skills,
                    'required_skills': required_skills
                })

            matches.sort(
                key=lambda job: job['match_percentage'],
                reverse=True
            )

        finally:
            cursor.close()
            connection.close()

    return render_template(
        'job_match.html',
        matches=matches,
        user_skills_text=user_skills_text,
        searched=searched
    )


















if __name__ == '__main__':
    app.run(debug=True)








































