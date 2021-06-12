import os
import streamlit as st
import pandas as pd 
from db_fxns import *
import json
import SessionState
import streamlit.components.v1 as stc

# Data Viz Pkgs
import plotly.express as px 


HTML_BANNER = """
    <div style="background-color:#464e5f;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;">ToDo App (CRUD)</h1>
    <p style="color:white;text-align:center;">Built with Streamlit</p>
    </div>
    """


def main():
	stc.html(HTML_BANNER)
	logout = st.button('Logout')
	config = dict()
	config['login_sign'] = 0
	if logout == 1:
		with open('config.json', 'w') as f:
			json.dump(config, f)

	menu = ["Create","Read","Update","Delete","About","Gantt","Notebook"]
	choice = st.sidebar.selectbox("Menu",menu)
	create_table()

	placeholder1 = st.empty()
	placeholder2 = st.empty()
	placeholder3 = st.empty()

	account = placeholder1.text_input('Your Account:')
	password = placeholder2.text_input('Your Password:', type='password')
	login_button = placeholder3.button('Login')

	if account == '123' and password == '123' and login_button:
		config['login_sign'] = 1
		with open('config.json', 'w') as f:
			json.dump(config, f)
		st.balloons()
		st.text('You have Logged in')

	with open('config.json', 'r') as f:
		config = json.load(f)
		login_sign = config['login_sign']

	if login_sign:
		placeholder1.empty()
		placeholder2.empty()
		placeholder3.empty()
		if choice == "Create":
			st.subheader("Add Item")
			col1,col2 = st.beta_columns(2)

			with col1:
				task = st.text_area("Task To Do")

			with col2:
				task_status = st.selectbox("Status",["ToDo","Doing","Done"])
				task_open_date = st.date_input("Open Date")
				task_due_date = st.date_input("Due Date")

			if st.button("Add Task"):
				add_data(task,task_status,task_open_date,task_due_date)
				st.success("Added ::{} ::To Task".format(task))


		elif choice == "Read":
			# st.subheader("View Items")
			with st.beta_expander("View All"):
				result = view_all_data()
				# st.write(result)
				clean_df = pd.DataFrame(result,columns=["Task","Status","Open Date","Due Date"])
				st.dataframe(clean_df)

			with st.beta_expander("Task Status"):
				task_df = clean_df['Status'].value_counts().to_frame()
				# st.dataframe(task_df)
				task_df = task_df.reset_index()
				st.dataframe(task_df)

				p1 = px.pie(task_df,names='index',values='Status')
				st.plotly_chart(p1,use_container_width=True)


		elif choice == "Update":
			st.subheader("Edit Items")
			with st.beta_expander("Current Data"):
				result = view_all_data()
				# st.write(result)
				clean_df = pd.DataFrame(result,columns=["Task","Status","Open Date","Due Date"])
				st.dataframe(clean_df)

			list_of_tasks = [i[0] for i in view_all_task_names()]
			selected_task = st.selectbox("Task",list_of_tasks)
			task_result = get_task(selected_task)
			# st.write(task_result)

			if task_result:
				task = task_result[0][0]
				task_status = task_result[0][1]
				task_open_date = task_result[0][2]
				task_due_date = task_result[0][3]

				col1,col2 = st.beta_columns(2)

				with col1:
					new_task = st.text_area("Task To Do",task)

				with col2:
					new_task_status = st.selectbox(task_status,["ToDo","Doing","Done"])
					new_task_open_date = st.date_input('task_open_date', key='open')
					new_task_due_date = st.date_input('task_due_date', key='close')

				if st.button("Update Task"):
					edit_task_data(new_task,new_task_status,new_task_open_date,new_task_due_date,
								   task,task_status,task_open_date,task_due_date)
					st.success("Updated ::{} ::To {}".format(task,new_task))

				with st.beta_expander("View Updated Data"):
					result = view_all_data()
					# st.write(result)
					clean_df = pd.DataFrame(result,columns=["Task","Status","Open Date","Due Date"])
					st.dataframe(clean_df)


		elif choice == "Delete":
			st.subheader("Delete")
			with st.beta_expander("View Data"):
				result = view_all_data()
				# st.write(result)
				clean_df = pd.DataFrame(result,columns=["Task","Status","Open Date","Due Date"])
				st.dataframe(clean_df)

			unique_list = [i[0] for i in view_all_task_names()]
			delete_by_task_name =  st.selectbox("Select Task",unique_list)
			if st.button("Delete"):
				delete_data(delete_by_task_name)
				st.warning("Deleted: '{}'".format(delete_by_task_name))

			with st.beta_expander("Updated Data"):
				result = view_all_data()
				# st.write(result)
				clean_df = pd.DataFrame(result,columns=["Task","Status","Open Date","Due Date"])
				st.dataframe(clean_df)

		elif choice == 'Gantt':
			import plotly.figure_factory as ff
			import plotly.graph_objects as go

			result = view_all_data()
			clean_df = pd.DataFrame(result,columns=["Task","Status","Start","Finish"])

			fig = ff.create_gantt(clean_df)

			st.plotly_chart(fig,use_container_width=True)

		elif choice == 'Notebook':
			lineNo = 0
			if os.path.exists('Notes.txt'):
				with open('Notes.txt', 'r') as f:
					notes = f.readlines()
					lineNo = len(notes)

			text = st.text_area("Note", height=400)
			col1, col2, col3 = st.beta_columns(3)

			with col1:
				upload_button = st.button('Upload')
			with col2:
				clear_button = st.button('Delete Notes')
			with col3:
				view_button = st.button("View Notes")

			if upload_button == 1:
				with open('Notes.txt', 'a') as f:
					text = text + '\n\n'
					f.write(text)
					st.success('Upload Successfully')
			if view_button:
				if os.path.exists('Notes.txt'):
					with open('Notes.txt', 'r') as f:
						notes = f.read()
					st.text(notes)
			if clear_button:
				os.remove('Notes.txt')
				st.success('Delete Successfully')


		else:
			st.subheader("About ToDo List App")
			st.info("Built with Streamlit")
			st.info("Jesus Saves @JCharisTech")
			st.text("Jesse E.Agbe(JCharis)")


if __name__ == '__main__':
	main()

