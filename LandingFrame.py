from tkinter import *
from tkinter import Canvas, Button, PhotoImage, ttk, messagebox, filedialog
from PIL import Image, ImageTk
import tkinter as tk
import pandas as pd
from datetime import datetime, date
import re

from matplotlib.figure import Figure
from matplotlib.patches import Wedge
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import FirebaseManager
import ReportFrames


class LandingFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bgimg = tk.PhotoImage(file="Resources/start_background.png")

        self.logo_bg = tk.PhotoImage(file="Resources/haifa-logo.png")

        self.firebase_manager = FirebaseManager.firebase_manager

        self.landing_frame = tk.Frame(self, width=1200, height=600)
        self.landing_frame.place(x=0, y=0)

        self.load_report_frame = tk.Frame(self, width=1200, height=600)

        self.credits_frame = tk.Frame(self, width=1200, height=600)

        self.monitor_frame = tk.Frame(self, width=1200, height=600, bg='#3c1d40')

        self.exam_db_data = None

        self.current_folder = -1

        # Creating Canvas
        self.canvas = Canvas(
            self.landing_frame,
            bg="#2A2F4F",
            height=600,
            width=1200,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        self.canvas.create_image(0, 0, anchor=NW, image=self.bgimg)

        self.canvas.place(x=0, y=0)

        welcome_message = """
     Welcome to ExamTrack!       
     Below are some instructions to help you get started:
            
     Starting the Exam:
     - Click on the "Start Exam" button to begin a new exam session.
     - Follow the on-screen prompts to set up exam parameters.
     - Once everything is set up, click "Continue" to initiate the
     exam process.
     - Use the face recognition feature to confirm attendance.
            
     Accessing Report History:
     - Click on the "View Reports" button to access past exam reports.
     - Browse through the list of available reports to find the one you're  
     interested in.
     - Click on a Load Report to view detailed information, including
     attendance records, break history, notes, and more.
     - Use the search and filter options to quickly find specific reports
            """
        help_msg = """
            Need Help?
            If you have any questions or encounter any issues while using 
            ExamTrack, don't hesitate to reach out to our support team for assistance.
            We're here to help make your exam management experience as smooth and 
            efficient as possible.
            """
        welcome_message_label = self.canvas.create_text(
            600.0,
            150.0,
            anchor="nw",
            text=welcome_message,
            fill="white",
            font=("Inter Bold", 18 * -1)
        )
        ReportFrames.text_add_border(self.canvas, welcome_message_label, 1, 'white')

        self.create_credits()

        exit_btn = Button(self.landing_frame, text='Exit', bd='5', fg="#FFFFFF", bg='#812e91',
                          font=("Calibri", 16 * -1),
                          activebackground='#917FB3', height='1', width='14',
                          command=lambda: self.controller.on_closing())
        exit_btn.place(x=390, y=410)

        credits_btn = Button(self.landing_frame, text='Credits', bd='5', fg="#FFFFFF", bg='#812e91',
                             font=("Calibri", 16 * -1),
                             activebackground='#917FB3', height='1', width='14',
                             command=lambda: self.show_credits())
        credits_btn.place(x=390, y=350)

        load_btn = Button(self.landing_frame, text='View Reports', bd='5', fg="#FFFFFF", bg='#812e91',
                          font=("Calibri", 16 * -1),
                          activebackground='#917FB3', height='1', width='14',
                          command=lambda: self.show_load_reports())
        load_btn.place(x=390, y=290)

        monitor_btn = Button(self.landing_frame, text='Exam Monitor', bd='5', fg="#FFFFFF", bg='#812e91',
                             font=("Calibri", 16 * -1),
                             activebackground='#917FB3', height='1', width='14',
                             command=lambda: self.show_monitor())
        monitor_btn.place(x=390, y=230)

        start_btn = Button(self.landing_frame, text='Start Exam', bd='5', fg="#FFFFFF", bg='#812e91',
                           font=("Calibri", 16 * -1),
                           activebackground='#917FB3', height='1', width='14',
                           command=lambda: self.controller.show_frame('StartPage'))
        start_btn.place(x=390, y=170)

    def reset_load_reports(self):
        self.load_report_frame.destroy()
        self.load_report_frame = tk.Frame(self, width=1200, height=600)

    def reset_monitor(self):
        self.monitor_frame.destroy()
        self.monitor_frame = tk.Frame(self, width=1200, height=600, bg='#3c1d40')

    def back_to_menu(self):
        self.load_report_frame.place_forget()
        self.monitor_frame.place_forget()
        self.credits_frame.place_forget()
        self.landing_frame.place(x=0, y=0)

    def show_load_reports(self):
        self.landing_frame.place_forget()
        self.load_report_frame.place(x=0, y=0)
        # Creating Canvas
        canvas = Canvas(
            self.load_report_frame,
            bg="#2A2F4F",
            height=600,
            width=1200,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.create_image(0, 0, anchor=NW, image=self.bgimg)

        canvas.place(x=0, y=0)

        canvas.create_rectangle(795, 285, 880, 370, fill='#917FB3', outline='black')

        # Function to retrieve list of folders from Firebase
        def get_folder_list():

            folder_list = []
            bucket = self.firebase_manager.get_bucket()
            folder_ref = bucket.list_blobs(prefix=f'{FirebaseManager.FIREBASE_REPORT_HISTORY_PATH}/')

            # Set to store processed folder names
            processed_folders = set()

            # Iterate over the items in the folder
            for f_item in folder_ref:
                # Extract the folder name from the object path
                folder_name = f_item.name.split('/')[1]  # Get the second part of the path as folder name

                pattern = re.compile(r'[^\w\s]+')

                # Remove non-printable characters using the pattern
                cleaned_folder_name = pattern.sub('', folder_name)

                if cleaned_folder_name in processed_folders:
                    continue

                # Define the regex pattern
                pattern = r'^Report_\d+_(MoedA|MoedB|MoedC)_(\d{2})(\d{2})(\d{2})$'
                # Check if folder name matches the pattern
                if not re.match(pattern, cleaned_folder_name):
                    # print(cleaned_folder_name)
                    continue

                # Extract exam number, term, and date from folder name
                parts = cleaned_folder_name.split('_')
                exam_number = parts[1]
                term = parts[2]
                date = parts[3]

                # Reformat date from DDMMYY to DD/MM/YY
                date = f"{date[:2]}/{date[2:4]}/{date[4:]}"

                # Add folder details to the list
                folder_list.append((exam_number, term, date, cleaned_folder_name))

                # Add the folder name to the processed folders set
                processed_folders.add(cleaned_folder_name)

            return folder_list

        # Create a Frame to contain the Treeview
        frame = ttk.Frame(self.load_report_frame, borderwidth=2, height=400, width=300)
        frame.pack_propagate(False)
        frame.place(x=380, y=170)

        def sort_by_date(row_data):
            # Custom comparison function for sorting by date
            return datetime.strptime(row_data[2], "%d/%m/%y")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=30, background="#917FB3", fieldbackground="#917FB3", foreground="white",
                        font=("Calibri", 14 * -1))
        style.configure("Treeview.Heading", rowheight=30, background="#917FB3", fieldbackground="#917FB3",
                        foreground="white", font=("Calibri", 14 * -1))
        style.map("Treeview.Heading", background=[("active", "#917FB3"), ("!active", "#917FB3")],
                  foreground=[("active", "white"), ("!active", "white")])
        style.map("Treeview", background=[("selected", "#000080")])

        # Create a table to display the folder list
        folder_table = ttk.Treeview(master=frame, columns=('Exam Number', 'Term', 'Date', 'Folder Name'),
                                    show='headings')
        folder_table.heading('Exam Number', text='Exam Number')
        folder_table.heading('Term', text='Term')
        folder_table.heading('Date', text='Date')
        folder_table.heading('Folder Name', text='Folder Name')

        folder_table.tag_configure('oddrow', background='#917FB3')
        folder_table.tag_configure('evenrow', background='#BAA4CA')

        folder_table["height"] = 10

        # Pack the Treeview
        folder_table.pack(side="left", fill="both", expand=True)

        # Get the list of folders from Firebase
        folders = get_folder_list()

        # Clear any existing data in the table
        for row in folder_table.get_children():
            folder_table.delete(row)

        color_j = 0
        # Populate the table with folder names
        for folder in sorted(folders, key=sort_by_date, reverse=True):
            color_tags = ('evenrow',) if color_j % 2 == 0 else ('oddrow',)
            folder_table.insert('', 'end', values=folder, tags=color_tags)
            color_j += 1
        folder_table.column('#1', width=100)
        folder_table.column('#2', width=100)
        folder_table.column('#3', width=100)
        folder_table.column('#4', width=50)

        def table_select_row(a):  # view selected row items
            cur_item = folder_table.focus()
            cur_values = folder_table.item(cur_item, option='values')
            if not cur_values:
                return
            self.current_folder = str(cur_values[3])

        folder_table.bind("<<TreeviewSelect>>", table_select_row)

        # Convert the table data to a pandas DataFrame
        data = []
        for item in folder_table.get_children():
            data.append(folder_table.item(item)['values'])

        df_backup = pd.DataFrame(data, columns=['id', 'Term', 'Date', 'Folder Name'])

        # Convert 'Date' column to datetime format
        df_backup['Date'] = pd.to_datetime(df_backup['Date'], format='%d/%m/%y')

        # Sort the DataFrame by 'Date'
        df_backup.sort_values(by='Date', inplace=True, ascending=False)

        # Format 'Date' column to display only 'dd/mm/yy'
        df_backup['Date'] = df_backup['Date'].dt.strftime('%d/%m/%y')

        # Convert to str for easier handling
        df_backup['Date'] = df_backup['Date'].astype(str)
        df_backup['id'] = df_backup['id'].astype(str)

        # Searching the table

        canvas.create_text(
            795,
            200,
            anchor="nw",
            text="Search Exam Number:",
            fill="#FFFFFF",
            font=("Calibri Bold", 18 * -1)
        )

        search_entry = tk.Entry(self.load_report_frame, width=20, bg="#917FB3", font=18, borderwidth=3)
        search_entry.place(x=795, y=235)

        # Search query and filter table
        def my_search(*args):
            table_df = df_backup

            query = search_entry.get().strip()  # get entry string
            str1 = table_df.id.str.contains(query, case=False)
            df2 = table_df[str1]

            r_set = df2.to_numpy().tolist()  # Create list of list using rows

            folder_table.delete(*folder_table.get_children())

            # Sort the filtered results based on the original order in df_backup
            sorted_results = sorted(r_set, key=lambda x: table_df[table_df['id'] == x[0]].index[0])

            j = 0  # similar to color j , counter for colouring purpose
            for dt in sorted_results:
                tags = ('evenrow',) if j % 2 == 0 else ('oddrow',)  # for colouring purpose
                v = [r for r in dt]  # creating a list from each row
                # Handling checkbox statuses
                s_id = v[0]
                s_term = v[1]
                if moeda_checkbox_var.get() == 1:
                    if str(s_term).lower() == 'moeda':
                        folder_table.insert("", "end", values=v, tags=tags)  # adding row
                        j += 1  # colouring
                if moedb_checkbox_var.get() == 1:
                    if str(s_term).lower() == 'moedb':
                        folder_table.insert("", "end", values=v, tags=tags)  # adding row
                        j += 1  # colouring
                if moedc_checkbox_var.get() == 1:
                    if str(s_term).lower() == 'moedc':
                        folder_table.insert("", "end", values=v, tags=tags)  # adding row
                        j += 1  # colouring
                if moedc_checkbox_var.get() == 0 and moedb_checkbox_var.get() == 0 and moeda_checkbox_var.get() == 0:
                    folder_table.insert("", "end", values=v, tags=tags)  # adding row
                    j += 1  # colouring

        search_entry.bind("<KeyRelease>", my_search)

        back_btn = tk.Button(self.load_report_frame, text='Back', bd='4', fg="#FFFFFF", bg='#812e91',
                             activebackground='#917FB3',
                             font=("Calibri", 16 * -1), height='1', width='14'
                             , command=lambda: [self.reset_load_reports(), self.back_to_menu()])
        back_btn.place(x=30, y=30)

        def load_btn_event():
            if self.current_folder == -1:
                return
            res = self.controller.frames["ReportFrames"].create_report(True, self.current_folder)
            if not res:
                messagebox.showerror("Load Report Error", "Failed to load report.")
            else:
                self.controller.show_frame("ReportFrames")

        # continue btn
        load_btn = Button(self.load_report_frame, text='Load Report', bd='5', fg="#FFFFFF", bg='#812e91',
                          font=("Calibri", 16 * -1),
                          activebackground='#917FB3', height='1', width='14',
                          command=load_btn_event)
        load_btn.place(x=795, y=410)

        # Checkboxes
        moeda_checkbox_var = IntVar()
        moeda_checkbox = Checkbutton(self.load_report_frame, variable=moeda_checkbox_var, onvalue=1, offvalue=0,
                                     height=1,
                                     font=("Inter Bold", 14 * -1), text="MoedA", bg="#917FB3",
                                     command=my_search)
        moeda_checkbox.place(x=800, y=290)

        moedb_checkbox_var = IntVar()
        moedb_checkbox = Checkbutton(self.load_report_frame, variable=moedb_checkbox_var, onvalue=1, offvalue=0,
                                     height=1,
                                     font=("Inter Bold", 14 * -1), text="MoedB", bg="#917FB3",
                                     command=my_search)
        moedb_checkbox.place(x=800, y=315)

        moedc_checkbox_var = IntVar()
        moedc_checkbox = Checkbutton(self.load_report_frame, variable=moedc_checkbox_var, onvalue=1, offvalue=0,
                                     height=1,
                                     font=("Inter Bold", 14 * -1), text="MoedC", bg="#917FB3",
                                     command=my_search)
        moedc_checkbox.place(x=800, y=340)

    def show_credits(self):
        self.landing_frame.place_forget()
        self.credits_frame.place(x=0, y=0)

    def create_credits(self):
        # Creating Canvas
        canvas = Canvas(
            self.credits_frame,
            bg="#2A2F4F",
            height=600,
            width=1200,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.create_image(0, 0, anchor=NW, image=self.bgimg)

        canvas.place(x=0, y=0)

        credits_text = """

Project Mentored by:
Dr. Rami Rashkovits

Project Team:
- Adnan Atili
- Haya Shalash
- Ameer Aburaya
"""

        more_info_text = """
Thanks to:
Department of Information Systems , Faculty and Staff of University of Haifa

About:
ExamTrack is a collaborative effort by a dedicated team of students from the
University of Haifa's Department of Information Systems. This project 
represents the culmination of our studies and showcases our passion for 
technology and innovation in education.

Contact Us:
For inquiries, feedback, or support regarding ExamTrack, please contact us at
 exam.track.haifa@gmail.com
"""
        canvas.create_text(
            400.0,
            100.0,
            anchor="nw",
            text=credits_text,
            fill="white",
            font=("Inter Bold", 18 * -1)
        )

        canvas.create_text(
            400.0,
            300.0,
            anchor="nw",
            text=more_info_text,
            fill="white",
            font=("Inter Bold", 16 * -1)
        )

        back_btn = tk.Button(self.credits_frame, text='Back', bd='4', fg="#FFFFFF", bg='#812e91',
                             activebackground='#917FB3',
                             font=("Calibri", 16 * -1), height='1', width='14'
                             , command=lambda: [self.back_to_menu()])
        back_btn.place(x=30, y=30)

    def show_monitor(self):

        self.landing_frame.place_forget()
        self.monitor_frame.place(x=0, y=0)
        self.monitor_frame.pack_propagate(False)

        # Ensure no border or highlight thickness for monitor_frame
        self.monitor_frame.config(bd=0, highlightthickness=0)

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        # Create a canvas and attach a scrollbar to it
        canvas = tk.Canvas(self.monitor_frame, bg='#3c1d40')
        canvas.pack(side="left", fill="both", expand=True, padx=0, pady=0)

        scrollbar = ttk.Scrollbar(canvas, orient="horizontal", command=canvas.xview)
        scrollbar.pack(side="bottom", fill="y", pady=55)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", on_configure)

        # Create a frame inside the canvas for exam cards
        frame = tk.Frame(canvas, bg='#3c1d40')
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Function to adjust the canvas scroll region
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        # Bind the function to the canvas resize event
        frame.bind("<Configure>", configure_scroll_region)

        # Display more info in a window
        def show_exam_info(exam_num_i):
            info_window = Toplevel(self.monitor_frame)
            info_window.geometry("800x600+150+30")
            info_window.resizable(False, False)
            info_window.title("Exam Info")
            info_window.configure(bg='#917FB3')

            info_frame = tk.Frame(info_window, width=400, height=600, bg='#333278', bd=3, relief='raised')
            info_frame.place(x=30, y=30)

            more_info_frame = tk.Frame(info_window, width=400, height=600, bg='#917FB3', bd=3, relief='ridge')
            more_info_frame.place(x=30, y=180)

            info_window_exam_label = Label(info_frame, text="   Exam Number: " + exam_num_i + "    ", bg='#333278',
                                           fg='white', font=("Inter Bold", 18 * -1))
            info_window_exam_label.pack()

            exam_info_i = self.exam_db_data.get(exam_num_i)
            if not exam_info_i:
                print(f"No data found for exam number: {exam_num_i}")
                return

            def format_key(word):
                # Remove underscores and capitalize the first letter of every word
                return ' '.join(word.capitalize() for word in word.split('_'))

            excluded_keys = ['date']
            exam_labels = {}

            for key, value in exam_info_i.items():
                # Skip keys in the excluded_keys list
                if key in excluded_keys:
                    continue
                formatted_key = format_key(key)
                label = tk.Label(info_window, text=f"{formatted_key}: {value}", bg='#917FB3',
                                 font=("Inter Bold", 18 * -1))
                exam_labels[key] = label

            # Add information labels
            exam_labels['term'].config(bg='#333278', fg='white')
            exam_labels['term'].pack(in_=info_frame)

            exam_labels['duration'].config(text=exam_labels['duration'].cget("text") + " Minutes", bg='#333278',
                                           fg='white')
            exam_labels['duration'].pack(in_=info_frame)

            status_title_label = tk.Label(info_window, text="Latest Status Update:", bg='#917FB3',
                                          font=("Inter Bold", 18 * -1))
            status_title_label.place(x=50, y=140)

            space_label = tk.Label(info_window, text="", bg='#917FB3', font=("Inter Bold", 18 * -1))
            space_label.pack(in_=more_info_frame, anchor="w", padx=5)

            exam_labels['current_attendance'].config(
                text=" " + exam_labels['current_attendance'].cget("text") + " Students ")
            exam_labels['current_attendance'].pack(in_=more_info_frame, anchor="w", padx=5)

            exam_labels['time_left'].config(text=" " + exam_labels['time_left'].cget("text") + " Minutes ")
            exam_labels['time_left'].pack(in_=more_info_frame, anchor="w", padx=5)

            exam_labels['added_time'].config(text=" " + exam_labels['added_time'].cget("text") + " Minutes ")
            exam_labels['added_time'].pack(in_=more_info_frame, anchor="w", padx=5)

            exam_labels['waiver_count'].config(text=" " + exam_labels['waiver_count'].cget("text") + " ")
            exam_labels['waiver_count'].pack(in_=more_info_frame, anchor="w", padx=5)

            exam_labels['notes_count'].config(text=" " + exam_labels['notes_count'].cget("text") + " ")
            exam_labels['notes_count'].pack(in_=more_info_frame, anchor="w", padx=5)

            exam_labels['breaks_count'].config(text=" " + exam_labels['breaks_count'].cget("text") + " ")
            exam_labels['breaks_count'].pack(in_=more_info_frame, anchor="w", padx=5)

            space_end_label = tk.Label(info_window, text="", bg='#917FB3', font=("Inter Bold", 18 * -1))
            space_end_label.pack(in_=more_info_frame, anchor="w", padx=5)

            # add attendance graph

            attendance_frame = tk.Frame(info_window, bd=3, relief=tk.RAISED, background='#dbc5db')
            attendance_frame.place(x=350, y=30)
            # Create a Figure instance
            fig = Figure(figsize=(3.5, 2.5))
            ax = fig.add_subplot(111)
            fig.patch.set_alpha(0)

            attended_perc = 0
            if exam_info_i['enlisted_count'] != 0:  # Avoiding Divide by 0
                attended_perc = round(exam_info_i["attendance_count"] / exam_info_i['enlisted_count'], 2)
            absent_perc = 1 - attended_perc
            # Pie chart parameters
            overall_ratios = [attended_perc, absent_perc]
            labels = ['Attended', 'Absent']
            explode = [0.1, 0]
            angle = -180 * overall_ratios[0]
            wedges, *_, texts = ax.pie(overall_ratios, autopct='%1.1f%%', startangle=angle, labels=labels,
                                       explode=explode,
                                       colors=['#1f77b4', 'red', '#2ca02c'])
            ax.set_title('Overall Attendance', fontsize='medium')

            # Set label size
            for text in texts:
                text.set_fontsize(12)

            # Convert the Figure to a Tkinter canvas
            attendance_canvas = FigureCanvasTkAgg(fig, master=attendance_frame)
            attendance_canvas._tkcanvas.config(background='#dbc5db')
            attendance_canvas.draw()
            attendance_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # place attendance details under the graph

            exam_labels['attendance_count'].place(x=350, y=290)
            exam_labels['enlisted_count'].place(x=350, y=320)

            # Create auto confirm percentage graph

            confirm_frame = tk.Frame(info_window, bd=3, relief=tk.RIDGE, background='#dbc5db')
            confirm_frame.place(x=350, y=365)

            # Bar chart parameters
            auto_perc = 0
            if exam_info_i["attendance_count"] != 0:  # Avoiding Divide by 0
                auto_perc = round(exam_info_i["auto_confirm_count"] / exam_info_i["attendance_count"], 2)
            auto_ratio = [auto_perc, 1 - auto_perc]
            waiver_labels = ['Auto', 'Manual']
            bottom = 1
            width = .2

            # Create a Figure
            fig2 = Figure(figsize=(3.5, 1.1))
            fig2.patch.set_alpha(0)

            # Create an Axes within the Figure
            ax2 = fig2.add_axes([0.1, 0.1, 0.8, 0.8])

            # Adding from the top matches the legend.
            for j, (height, label) in enumerate(reversed([*zip(auto_ratio, waiver_labels)])):
                bottom -= height
                bc = ax2.barh(0, height, width, left=bottom, color='green', label=label,
                              alpha=0.3 + 0.5 * j, edgecolor='black')
                ax2.bar_label(bc, labels=[f"{height:.0%}"], label_type='center')

            ax2.set_title('Confirm Method Percentage', fontsize='small', loc='center', pad=-0, y=0.85)
            ax2.legend(loc='center', bbox_to_anchor=(0.5, 0.1), fontsize='small', ncol=2)
            ax2.axis('off')
            ax2.set_ylim(- 2.5 * width, 2.5 * width)

            # Convert the Figure to a Tkinter canvas
            confirm_canvas = FigureCanvasTkAgg(fig2, master=confirm_frame)
            confirm_canvas._tkcanvas.config(background='#dbc5db')
            confirm_canvas.draw()
            confirm_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # count labels

            exam_labels['auto_confirm_count'].place(x=350, y=490)
            exam_labels['manual_confirm_count'].place(x=350, y=520)

            info_window_done_btn = Button(info_window, text='Done', bd='5', fg="#FFFFFF", bg='#812e91'
                                          , font=("Calibri", 16 * -1), activebackground='#917FB3', height='1',
                                          width='14', disabledforeground='gray', command=info_window.destroy)
            info_window_done_btn.place(x=115, y=450)

        def create_overview_card(parent, exam_info_i, color_i):
            if color_i % 2 == 0:
                card_bg = '#8b77a7'
            else:
                card_bg = '#dbc5db'

            # Create a frame to contain the card
            card_frame = tk.Frame(parent, bg=card_bg, bd=5, relief="groove", cursor="hand2")
            card_frame.pack(anchor="nw", side='left', fill='both', padx=20, pady=150)

            # Bind the label to the label_clicked function when clicked
            card_frame.bind("<Button-1>", lambda event: show_exam_info(exam_info_i['Exam Number']))

            label = tk.Label(card_frame, text=" ", bg=card_bg, font=("Inter Bold", 18 * -1))
            label.pack(anchor="w", padx=5, pady=2)
            # Add exam information to the card
            for key, value in exam_info_i.items():
                label = tk.Label(card_frame, text=f"    {key}: {value}    ", bg=card_bg, font=("Inter Bold", 18 * -1))
                label.pack(anchor="w", padx=5, pady=2)
            label = tk.Label(card_frame, text=" ", bg=card_bg, font=("Inter Bold", 18 * -1))
            label.pack(anchor="w", padx=5, pady=2)

            return

        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y")

        self.exam_db_data = self.firebase_manager.get_exam_status_by_date(dt_string)

        exam_info_list = []

        if self.exam_db_data:
            for exam_number, data in self.exam_db_data.items():
                if str(data.get("status", "")).lower() == 'finished':
                    continue
                exam_info = {
                    "Exam Number": exam_number,
                    "Term": data.get("term", ""),
                    "Time Left": str(data.get("time_left", "")) + " Minutes",
                    "Currently Attending": str(data.get("current_attendance", "")) + " Students",
                    "Status": data.get("status", "")
                }
                exam_info_list.append(exam_info)

        c = 0
        # Create overview cards for each exam
        for exam_info in exam_info_list:
            overview_card = create_overview_card(frame, exam_info, c)
            c += 1
        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        heading_label = tk.Label(self.monitor_frame, text="Ongoing Exams", fg='white', bg='#3c1d40',
                                 font=("Calibri Bold", 28 * -1))
        heading_label.place(x=480, y=30)

        date_label = tk.Label(self.monitor_frame, text=d1, fg='white', bg='#3c1d40',
                              font=("Calibri Bold", 24 * -1), bd=1)
        date_label.place(x=510, y=70)

        panel_logo = tk.Label(self.monitor_frame, bd=0)
        panel_logo.place(x=15, y=455)
        panel_logo.configure(image=self.logo_bg)
        panel_logo.tkraise()

        # Refresh Functionality

        def refresh_data(f_info_list):
            # Get current date
            now_f = datetime.now()
            dt_string_f = now_f.strftime("%d-%m-%Y")

            # Retrieve exam data from Firebase again
            self.exam_db_data = self.firebase_manager.get_exam_status_by_date(dt_string_f)

            # Clear existing cards
            for widget in frame.winfo_children():
                widget.destroy()

            f_info_list = []
            if self.exam_db_data:
                for exam_number_f, data_f in self.exam_db_data.items():
                    if str(data_f.get("status", "")).lower() == 'finished':
                        continue
                    exam_info_f = {
                        "Exam Number": exam_number_f,
                        "Term": data_f.get("term", ""),
                        "Time Left": str(data_f.get("time_left", "")) + " Minutes",
                        "Currently Attending": str(data_f.get("current_attendance", "")) + " Students",
                        "Status": data_f.get("status", "")
                    }
                    f_info_list.append(exam_info_f)

            c_f = 0
            # Create overview cards for each exam
            for exam_info_f in f_info_list:
                create_overview_card(frame, exam_info_f, c_f)
                c_f += 1

        refresh_btn = tk.Button(self.monitor_frame, text='Refresh', bd='4', fg="#FFFFFF", bg='#812e91',
                                activebackground='#917FB3',
                                font=("Calibri", 16 * -1), height='1', width='14'
                                , command=lambda: [refresh_data(exam_info_list)])
        refresh_btn.place(x=400, y=515)

        back_btn = tk.Button(self.monitor_frame, text='Back', bd='4', fg="#FFFFFF", bg='#812e91',
                             activebackground='#917FB3',
                             font=("Calibri", 16 * -1), height='1', width='14'
                             , command=lambda: [self.reset_monitor(), self.back_to_menu()])
        back_btn.place(x=30, y=30)
