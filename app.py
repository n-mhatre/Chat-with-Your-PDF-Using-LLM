import streamlit as st
import sqlite3
import pandas as pd
st.set_page_config(layout="wide")
css = '''
<style>
    [data-testid="stSidebar"]{
        min-width: 400px;
        max-width: 1000px;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)



db_path = 'ADT_Project.db'  # Replace with your database path

# Function to connect to the SQLite database
def connect_to_db(path):
    conn = sqlite3.connect(path)
    return conn

# Function to fetch data from a table
def fetch_data(query, conn, params=None):
    return pd.read_sql_query(query, conn, params=params)

# Function to insert a job post record into the JobPost table
def insert_job_post(conn, job_post_data):
    cursor = conn.cursor()
    query = '''
    INSERT INTO JobPost (ID, title, term, duration, jobdescription, jobrequirement, requiredqualification, salary, isIT, isPosted,companyid)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(query, job_post_data)
    conn.commit()

# Function to get a single job post record by ID
def get_job_post_by_id(conn, job_id):
    cursor = conn.cursor()
    query = '''SELECT ID, Title, Term, Duration, JobDescription, JobRequirement, RequiredQualification, Salary, isIT, 
             isPosted, companyid, locationID, timelineID, additional_InfoID FROM JobPost WHERE id = ?'''
    cursor.execute(query, (job_id,))
    return cursor.fetchone()

# Function to update a job post record in the JobPost table
def update_job_post(conn, job_id, update_data):
    cursor = conn.cursor()
    query = '''
    UPDATE JobPost
    SET title = ?, term = ?, duration = ?, jobdescription = ?, jobrequirement = ?, requiredqualification = ?, salary = ?, isIT = ?, isPosted = ?
    WHERE id = ?
    '''
    cursor.execute(query, update_data + (job_id,))
    conn.commit()


def deleteOperation(id, conn):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        delete_query = "DELETE FROM JobPost WHERE ID = {}".format(id)
        cursor.execute(delete_query)
        conn.commit()
        st.success('Job id: {},This is succefully deleted !!'.format(id), icon="✅")
    except Exception as e:
        print(e)
        st.info('Job id: {},This is already deleted.'.format(id), icon="ℹ️")



# Function to check if the company exists and return its ID or create a new one
def get_or_create_company(conn, company_name, about_text):
    cursor = conn.cursor()
    # Check if company already exists
    cursor.execute('SELECT ID FROM Company WHERE name = ?', (company_name,))
    result = cursor.fetchone()
    if result:
        return result[0]  # Return the existing company ID
    else:
        # Insert new company since it does not exist
        cursor.execute('INSERT INTO Company (name, about) VALUES (?, ?)', (company_name, about_text))
        conn.commit()
        return cursor.lastrowid  # Return the new company ID

def update_job_post_fields(conn, job_id, update_data):
    cursor = conn.cursor()
    # Construct the SQL update query dynamically based on the fields provided in update_data
    set_clause = ', '.join([f"{k} = ?" for k in update_data])
    query = f"UPDATE JobPost SET {set_clause} WHERE ID = ?"
    params = list(update_data.values()) + [job_id]
    cursor.execute(query, params)
    conn.commit()


def showData(col2, row):
    with col2.container(border=True):
        st.write('<center><h3>Job id:{} - {}</h3></center>'.format(row['id'], row.title), unsafe_allow_html=True)
        st.write('<center><h3>{}</center></h3>'.format(row.cname), unsafe_allow_html=True)
        if row.location:
            st.write('location: {}'.format(row.location))
        st.text('postdate: {} \nstartdate: {} \ndeadline: {} \nopeningdate: {}'.format(str(row.postDate), row.startDate, row.deadline, row.openingDate))
        if row.cabout:
            st.text('about company: \n{}'.format(row.cabout))
        if row.jobdescription:
            st.write('#')
            st.write('<h5>Job Description:</h5>', unsafe_allow_html=True)
            st.write(row.jobdescription)
        if row.jobrequirement:
            st.write('#')
            st.write('<h5>Job Requirement:</h5>', unsafe_allow_html=True)
            st.write(row.jobrequirement)
        if row.requiredqualification:
            st.write('#')
            st.write('<h5>Required Qualification:</h5>', unsafe_allow_html=True)
            st.write(row.requiredqualification)


# Function to insert a job post record into the JobPost table
def insert_job_post(conn, job_post_data):
    cursor = conn.cursor()
    query = '''
    INSERT INTO JobPost (title, term, duration, jobdescription, jobrequirement, requiredqualification, salary, isIT, isPosted,companyid, locationId)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(query, job_post_data)
    conn.commit() 

# Streamlit app layout  
def main():
    st.title("Job Connect Recruitment Portal")

    # Connect to the SQLite database
    db_path = 'ADT_Project.db'  # Replace with your database path
    conn = connect_to_db(db_path)

    # Sidebar for CRUD operations
    st.sidebar.title("Operations to perform")
    operation = st.sidebar.radio("Choose an operation", ["Create", "Read", "Update", "Delete", 'Check jobs'])

    if operation == "Create":
        # Implement Create operation fields and logic
        st.subheader("Create a New Job Posting")

        # Fetch locations for the dropdown
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Location")
        locations =  cursor.fetchall()

        cursor = conn.cursor()
        cursor.execute("SELECT ID, name FROM Company")
        companies = cursor.fetchall()            

        # Create a dictionary with location names as keys and their IDs as values
        location_options = {'': None}  # Start with an empty option
        company_options = {'': None}  # Start with an empty option for companies

        location_options.update({name: loc_id for loc_id, name in locations})
        company_options.update({name: comp_id for comp_id, name in companies})

        # Form for adding a new job post
        with st.form(key='new_job_post'):
            st.write("Add a New Job Post")
            #id = st.number_input('id')
            title = st.text_input('Title')
 
            # Dropdown for selecting company
            selected_company_name = st.selectbox('Company', options=list(company_options.keys()))
            # Get the companyID from the selected company name
            selected_company_id = company_options[selected_company_name]

            # Dropdown for selecting location
            selected_location_name = st.selectbox('Location', options=list(location_options.keys()))
            # Get the locationId from the selected location name
            selected_location_id = location_options[selected_location_name]


            term = st.text_area('Term')
            duration = st.text_area('Duration')
            jobdescription = st.text_area('Job Description')
            jobrequirement = st.text_area('Job Requirement')
            requiredqualification = st.text_area('Required Qualification')
            salary = st.text_input('Salary')
            isIT = st.checkbox('Is IT')
            isPosted = st.checkbox('Is Posted', value=False)
            
            submit_button = st.form_submit_button(label='Submit Job Post')
            if submit_button:
                if selected_company_id is not None and selected_location_id is not None:
                    job_post_data = (
                        title, term, duration, jobdescription, jobrequirement,
                        requiredqualification, salary, isIT, isPosted,selected_company_id,selected_location_id
                        )
                    insert_job_post(conn, job_post_data)
                    st.success("The job post has been added successfully!")
                else:
                    st.error("Please select a location/company.")        

    elif operation == "Read":
        # Implement Read operation
        st.subheader("View Records")
        # Example to view job postings
        jobposts_query = "SELECT * FROM JobPost order by id desc limit 100"
        jobposts_data = fetch_data(jobposts_query, conn)
        st.data_editor(jobposts_data, hide_index=True)

    elif operation == "Update":
        st.subheader("Update a Job Post")
        job_id = st.number_input("Enter the Job Post ID to update", min_value=1, format="%d")

        # Load the job post data when the button is clicked and store it in the session state
        if st.button('Load Job Post'):
            st.session_state.job_post_data = get_job_post_by_id(conn, job_id)
            if st.session_state.job_post_data:
                job_post_df = pd.DataFrame([st.session_state.job_post_data], columns=['ID', 'Title', 'Term', 'Duration', 'JobDescription', 'JobRequirement', 'RequiredQualification', 'Salary', 'isIT', 'isPosted', 'companyid', 'locationID', 'timelineID', 'additional_InfoID'])
                st.table(job_post_df)
            else:
                st.error("Job Post not found. Please enter a valid Job Post ID.")

        # Proceed with the update only if the job post data is loaded
        if 'job_post_data' in st.session_state and st.session_state.job_post_data:
            with st.form(key='update_job_post_form'):
                new_title = st.text_input('Title', value=st.session_state.job_post_data[1])
                new_term = st.text_area('Term', value=st.session_state.job_post_data[2])
                new_duration = st.text_area('Duration', value=st.session_state.job_post_data[3])
                new_jobdescription = st.text_area('Job Description', value=st.session_state.job_post_data[4])
                new_jobrequirement = st.text_area('Job Requirement', value=st.session_state.job_post_data[5])
                new_requiredqualification = st.text_area('Required Qualification', value=st.session_state.job_post_data[6])
                new_salary = st.text_input('Salary', value=str(st.session_state.job_post_data[7]))
                new_isIT = st.checkbox('Is IT', value=bool(st.session_state.job_post_data[8]))
                new_isPosted = st.checkbox('Is Posted', value=bool(st.session_state.job_post_data[9]))

                submit_update = st.form_submit_button('Update Job Post')

            if submit_update:
                update_query = '''
                        UPDATE JobPost
                        SET Title = ?, Term = ?, Duration = ?, JobDescription = ?, JobRequirement = ?, RequiredQualification = ?, Salary = ?, isIT = ?, isPosted = ?
                        WHERE ID = ?'''
                update_values = (new_title, new_term, new_duration, new_jobdescription, new_jobrequirement,
                             new_requiredqualification, new_salary, new_isIT, new_isPosted, job_id)
            
                cursor = conn.cursor()
                cursor.execute(update_query, update_values)
                conn.commit()
                st.success("Job post updated successfully.")
                # Clear the session state after updating
                del st.session_state.job_post_data
    
    elif operation=='Delete':
        st.subheader('select which job post you want to delete ..!!')
        st.write('#')
        query = """
                        SELECT j.id, c.name as cname, j.title
                        FROM JobPost j
                            left join company c on c.id=j.companyid
                        order by j.id desc
                        limit 50
                        """
        jobposts_data = fetch_data(query, conn)
        for index, row in jobposts_data.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([4,1])
                # Add elements to each column
                with col1.container(border=False):
                    scol1, scol2 = st.columns([1,4])
                    scol1.write('<h3>Job id: {} </h3>'.format(row['id']), unsafe_allow_html=True)
                    #scol1.subheader('Job id:1')
                    scol2.write('<h4>{}</h4>'.format(row['cname']), unsafe_allow_html=True)
                    scol2.write('<h5>{}</h5>'.format(row['title']), unsafe_allow_html=True)
                col2.button("Delete"
                            , key='delete_button_'+str(row['id'])
                            , use_container_width=True
                            , on_click = deleteOperation
                            , args=(row['id'],conn)
                            )
                
    elif operation=='Check jobs':
        st.subheader('Job list:')
        st.write('#')

        query = """
                        SELECT j.id, c.name as cname, c.about as cabout, j.title, l.name as location 
                            , t.postDate, t.startDate, t.deadline, t.openingDate
                            , j.jobdescription, j.jobrequirement, j.requiredqualification
                        FROM JobPost j
                            left join company c on c.id=j.companyid
                            left join location l on l.id = j.locationid
                            left join timeline t on t.id = j.timelineid
                        -- group by 2,3,4,5,6, 7
                        order by  j.id desc
                        limit 500
                        """
        jobposts_data = fetch_data(query, conn)
        jobposts_data = jobposts_data.drop_duplicates(subset=['title', 'location' , 'postDate', 'startDate', 'deadline', 'openingDate']).head(50)
        with st.container(border=False):
            #id=21
            col1, col2 = st.columns([1,5], gap='medium')
            # Add elements to each column
            with col1.container(border=True):
                for index, row in jobposts_data.iterrows():
                    st.button('job: '+str(row['id'])#+row['cname']+row['title']
                                , key='show_button_'+str(row['id'])
                                , use_container_width=True, on_click=showData
                                , args=(col2,row)
                                )


    conn.close()

if __name__ == "__main__":
    main()
 