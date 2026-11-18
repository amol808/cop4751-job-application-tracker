#### Job Application Tracker

COP4751 – Advanced Database Management

Course Project





#### Project Overview

For this project, I built a web application to keep track of information during a job search. The application lets users organize companies, job postings, applications and professional contacts in one place instead of keeping the information in separate files.

I used MySQL for the database, Python and Flask for the backend, and HTML, CSS and Bootstrap for the website. I also added a Job Match page that compares skills entered by a user with the required skills saved for different jobs.





#### Technologies Used

* Python 3 and Flask
* MySQL and MySQL Workbench
* HTML, CSS, Bootstrap, and Jinja2 templates
* mysql-connector-python and python-dotenv
* Git and GitHub





#### Features

**Dashboard:** Shows the number of companies, jobs, applications and contacts in the database.

**Companies:** Add, view, edit and delete company information, including names, industries, websites and locations.

**Jobs:** Keep track of job postings and connect them to companies. Job details can include a title, description, type, salary range, posting URL, date, active status and requirements stored as JSON.

**Applications:** Track applications for specific jobs, including the application date, status, résumé version, whether a cover letter was sent, interview information and notes.

**Contacts:** Store professional contacts connected to companies, along with their names, job titles, email addresses, phone numbers, LinkedIn links, and notes.

**Job Match:** Enter skills separated by commas to see which jobs are the closest match. The application checks the `required\_skills` list in each job's JSON requirements and uses this calculation:

`Match percentage = (matching required skills / total required skills) × 100`

Results are shown from highest to lowest percentage and include both matching and missing skills. Jobs without a valid required-skills list are not included in the results.





#### Database Design

The MySQL database contains four main tables. The `companies` table stores information about employers. The `jobs` table stores job postings, with each job linked to a company through `company\_id`. The `applications` table stores application records and links each application to a job through `job\_id`. The `contacts` table stores contact information and links each contact to a company through `company\_id`.

These relationships use foreign keys to connect the records. The `jobs` table also has a JSON column named `requirements`, and the `applications` table has a JSON column named `interview\_data`. The database structure is included in `schema.sql`. Sample records may need to be added separately after importing the schema.







#### Project Files

```text
job\_tracker\_project/
├── app.py
├── database.py
├── schema.sql
├── sample\_data.sql
├── requirements.txt
├── README.md
├── AI\_USAGE.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── companies.html
│   ├── company\_form.html
│   ├── jobs.html
│   ├── job\_form.html
│   ├── applications.html
│   ├── application\_form.html
│   ├── contacts.html
│   ├── contact\_form.html
│   └── job\_match.html
└── static/
    └── style.css
```

The `.env` file is used locally for database settings and is not included in the GitHub repository.







#### How to Run the Project

**1. Install the required software.** Install Python 3 and MySQL Server. MySQL Workbench can be used to import the schema and view the database.

**2. Get the project files.** Clone the GitHub repository or download its ZIP file and open a Command Prompt or terminal in the project folder.

**3. Install the Python packages.** Run:

```bash
py -m pip install -r requirements.txt
```

On a system without the Windows `py` launcher, use `python3 -m pip` instead. The main packages are Flask, mysql-connector-python, and python-dotenv.

**4. Set up the database.** Start MySQL and import `schema.sql` using MySQL Workbench. Make sure the database is named `job\_tracker` and that the MySQL account has permission to work with its tables. If the schema file does not create the database automatically, create it before importing the tables.

**5. Configure the database connection.** Create a `.env` file in the main project folder with the settings needed by `database.py` and a Flask secret key. An example is shown below; the variable names must match those used in `database.py`.

```dotenv
DB\_HOST=localhost
DB\_USER=root
DB\_PASSWORD=your\_mysql\_password
DB\_NAME=job\_tracker
SECRET\_KEY=replace\_with\_a\_long\_random\_secret
```

Do not upload `.env` to GitHub because it contains local credentials.

**6. Start the website.** Run:

```bash
py app.py
```

Then open `http://127.0.0.1:5000` in a browser. The navigation bar provides access to all six pages.





#### Testing

I tested adding, viewing, updating and deleting records in Companies, Jobs, Applications and Contacts. I used temporary test records for these checks and removed them afterward. I also tested Job Match using `Python, SQL, Flask, Git`. With the job requirements stored in the database, Software Developer returned a 100% match (3 out of 3 required skills), while Data Analyst returned a 33% match (1 out of 3).





#### Project Notes

This application was built for a course project and runs locally with Flask and MySQL. It has not been deployed as a public website.

