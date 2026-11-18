#### AI Usage Documentation

COP4751 – Advanced Database Management  
Job Application Tracker – Course Project





#### Tools Used

I used ChatGPT as a development and learning tool while building my Job Application Tracker. It helped me with Python and Flask code, SQL queries, HTML templates, troubleshooting errors and explanations of how the different parts of the application work. I used ChatGPT for this project rather than other AI tools.





#### Key Prompts and Questions

Some examples of questions I asked during development were:

1. How can I connect my Flask application to the MySQL database I already created?
2. Help me create Flask routes and HTML forms for adding, viewing, editing and deleting records in the companies, jobs, applications and contacts tables.
3. Why am I getting a Flask `BuildError` when I click the Add Company button?
4. How should I organize the routes in `app.py' and where should the new code go?
5. How can I compare skills entered by a user with the `required\_skills` list stored in a JSON column and calculate a match percentage?
6. Can you help me check the README and setup instructions against the project requirements?

These are representative examples; some of my questions included screenshots, code I was working with or error messages.





#### What Worked Well

ChatGPT helped generate much of the initial code for the Flask routes and HTML templates. This was useful for building the forms and CRUD operations for all four tables. It also helped with SQL queries that display information from related tables, such as showing a company name next to a job posting.

The Job Match feature was another area where AI assistance was useful. ChatGPT helped create the logic to compare a user's skills with the required skills stored in each job's JSON data, calculate the percentage and display matching and missing skills.

I also used it to troubleshoot problems as I worked. For example, when the Companies page gave me a Flask `BuildError`, I reviewed the route and template setup and checked that the updated files were saved correctly.





#### What I Changed and Tested

I worked with the MySQL database and checked the column names in MySQL Workbench so that the generated code matched my actual tables. For example, my jobs table uses `posting\_url` and my contacts table stores `first\_name` and `last\_name` separately. I shared those details and updated the project files accordingly.

I added the code to my local Flask project, organized the Python and HTML files, corrected formatting and file-saving issues and tested the pages in my browser. For each table, I added a temporary record, edited it and deleted it to verify that the CRUD operations worked with MySQL.

I also tested Job Match by entering `Python, SQL, Flask, Git`. The Software Developer job returned 100% because all three required skills matched. The Data Analyst job returned 33% because one of its three required skills matched. I checked these results against the JSON requirements in the database.





#### Lessons Learned

This project helped me understand how Flask routes, HTML templates and MySQL queries work together. I also learned more about using Jinja2 to display records, connecting tables with foreign keys, and reading required skills from JSON data.

The biggest lesson was that AI-generated code still has to be checked and tested. A route name or database column that does not match the actual project can prevent a page from working. Using ChatGPT helped me develop the application, but I still had to set it up locally, work through errors and verify the features myself.

