import mysql.connector
from mysql.connector import Error
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import datetime
import random
import os

class MovieBookingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Ticket Booking System")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#2c3e50")
        
        # Database connection
        self.connection = self.connect_to_database()
        
        # Colors and fonts
        self.bg_color = "#2c3e50"
        self.fg_color = "#ecf0f1"
        self.accent_color = "#e74c3c"
        self.highlight_color = "#3498db"
        self.font_large = ("Helvetica", 16)
        self.font_medium = ("Helvetica", 12)
        self.font_small = ("Helvetica", 10)
        
        # Create GUI
        self.create_main_frame()
        
    def connect_to_database(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',  # replace with your MySQL username
                password='1234',  # replace with your MySQL password
                database='movie_booking'
            )
            if connection.is_connected():
                print("Connected to MySQL database")
                return connection
        except Error as e:
            messagebox.showerror("Database Error", f"Error connecting to MySQL: {e}")
            return None
    
    def create_main_frame(self):
        # Main container
        self.main_frame = Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Header
        header = Frame(self.main_frame, bg=self.accent_color, height=80)
        header.pack(fill=X)
        
        title = Label(header, text="CINEMA HUB", font=("Helvetica", 24, "bold"), 
                     bg=self.accent_color, fg="white")
        title.pack(pady=20)
        
        # Navigation buttons
        nav_frame = Frame(self.main_frame, bg=self.bg_color)
        nav_frame.pack(fill=X, padx=20, pady=10)
        
        self.movies_btn = Button(nav_frame, text="Movies", font=self.font_medium,
                                bg=self.highlight_color, fg="white", bd=0,
                                command=self.show_movies)
        self.movies_btn.pack(side=LEFT, padx=10)
        
        self.bookings_btn = Button(nav_frame, text="My Bookings", font=self.font_medium,
                                  bg=self.bg_color, fg=self.fg_color, bd=0,
                                  command=self.show_my_bookings)
        self.bookings_btn.pack(side=LEFT, padx=10)
        
        # Content area
        self.content_frame = Frame(self.main_frame, bg=self.bg_color)
        self.content_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Show movies by default
        self.show_movies()
    
    def show_movies(self):
        # Reset buttons
        self.movies_btn.config(bg=self.highlight_color)
        self.bookings_btn.config(bg=self.bg_color)
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Title
        title = Label(self.content_frame, text="Now Showing", font=self.font_large,
                      bg=self.bg_color, fg=self.fg_color)
        title.pack(pady=10)
        
        # Add Movie button
        add_movie_btn = Button(self.content_frame, text="Add Movie", font=self.font_small,
                               bg=self.accent_color, fg="white", bd=0,
                               command=self.show_add_movie_form)
        add_movie_btn.pack(anchor=NE, pady=(0, 10), padx=10)
        
        # Fetch movies from database
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM movies WHERE is_active = TRUE")
            movies = cursor.fetchall()
            
            if not movies:
                no_movies = Label(self.content_frame, text="No movies available at the moment.",
                                 font=self.font_medium, bg=self.bg_color, fg=self.fg_color)
                no_movies.pack(pady=50)
                return
            
            # Create a frame for movie cards
            movies_frame = Frame(self.content_frame, bg=self.bg_color)
            movies_frame.pack(fill=BOTH, expand=True)
            
            # Display movies in a grid
            row, col = 0, 0
            for movie in movies:
                movie_card = Frame(movies_frame, bg="#34495e", bd=2, relief=RAISED)
                movie_card.grid(row=row, column=col, padx=15, pady=15)
                
                # Movie poster
                poster_frame = Frame(movie_card, bg="#34495e", width=180, height=250)
                poster_frame.pack(padx=10, pady=10)
                poster_frame.pack_propagate(False)
                try:
                    img_path = movie[5] if movie[5] and os.path.exists(movie[5]) else 'the.jpg'
                    img = Image.open(img_path)
                    img = img.resize((180, 250), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    poster = Label(poster_frame, image=photo, bg="#34495e")
                    poster.image = photo
                    poster.pack()
                except:
                    poster = Label(poster_frame, text="No Image", bg="#34495e", fg="white")
                    poster.pack(expand=True)
                
                # Movie title
                title = Label(movie_card, text=movie[1], font=self.font_small, 
                             bg="#34495e", fg="white", wraplength=180)
                title.pack(padx=5, pady=(0, 5))
                
                # Movie details button
                details_btn = Button(movie_card, text="View Details", font=self.font_small,
                                     bg=self.highlight_color, fg="white", bd=0,
                                     command=lambda m=movie: self.show_movie_details(m))
                details_btn.pack(pady=(0, 5))
                
                # Edit button
                edit_btn = Button(movie_card, text="Edit", font=self.font_small,
                                  bg="#27ae60", fg="white", bd=0,
                                  command=lambda m=movie: self.show_edit_movie_form(m))
                edit_btn.pack(pady=(0, 5))
                
                # Delete button
                delete_btn = Button(movie_card, text="Delete", font=self.font_small,
                                    bg="#e74c3c", fg="white", bd=0,
                                    command=lambda m=movie: self.delete_movie(m[0]))
                delete_btn.pack(pady=(0, 5))
                
                col += 1
                if col > 3:
                    col = 0
                    row += 1
                    
        except Error as e:
            messagebox.showerror("Database Error", f"Error fetching movies: {e}")
    
    def show_add_movie_form(self):
        form_win = Toplevel(self.root)
        form_win.title("Add New Movie")
        form_win.geometry("400x550")
        form_win.grab_set()

        Label(form_win, text="Title:").pack(anchor=W, padx=20, pady=(20, 0))
        title_entry = Entry(form_win, width=40)
        title_entry.pack(padx=20)

        Label(form_win, text="Genre:").pack(anchor=W, padx=20, pady=(10, 0))
        genre_entry = Entry(form_win, width=40)
        genre_entry.pack(padx=20)

        Label(form_win, text="Duration (mins):").pack(anchor=W, padx=20, pady=(10, 0))
        duration_entry = Entry(form_win, width=40)
        duration_entry.pack(padx=20)

        Label(form_win, text="Rating:").pack(anchor=W, padx=20, pady=(10, 0))
        rating_entry = Entry(form_win, width=40)
        rating_entry.pack(padx=20)

        Label(form_win, text="Image Path:").pack(anchor=W, padx=20, pady=(10, 0))
        image_entry = Entry(form_win, width=30)
        image_entry.pack(side=LEFT, padx=(20,0))
        def browse_image():
            file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.gif")])
            if file_path:
                image_entry.delete(0, END)
                image_entry.insert(0, file_path)
        browse_btn = Button(form_win, text="Browse", command=browse_image)
        browse_btn.pack(side=LEFT, padx=(5,0))
        Frame(form_win).pack(fill=X)

        Label(form_win, text="Description:").pack(anchor=W, padx=20, pady=(10, 0))
        desc_text = Text(form_win, width=30, height=5)
        desc_text.pack(padx=20)

        is_active_var = IntVar(value=1)
        Checkbutton(form_win, text="Active", variable=is_active_var).pack(anchor=W, padx=20, pady=(10, 0))

        def save():
            title = title_entry.get()
            genre = genre_entry.get()
            duration = duration_entry.get()
            rating = rating_entry.get()
            image_path = image_entry.get().strip()
            desc = desc_text.get("1.0", "end-1c")
            is_active = is_active_var.get()
            if not title or not genre or not duration or not rating:
                messagebox.showerror("Error", "Please fill all required fields!")
                return
            try:
                duration_int = int(duration)
            except ValueError:
                messagebox.showerror("Error", "Duration must be a number!")
                return
            # Handle image copy and rename by movie title
            if image_path:
                try:
                    ext = os.path.splitext(image_path)[1]
                    safe_title = title.strip().replace(' ', '_')
                    import re
                    safe_title = re.sub(r'[^A-Za-z0-9_]', '', safe_title)
                    img_filename = f"{safe_title}{ext}"
                    dest_path = os.path.join("images", img_filename)
                    if not os.path.exists("images"):
                        os.makedirs("images")
                    from shutil import copyfile
                    copyfile(image_path, dest_path)
                    db_image_path = dest_path
                except Exception as e:
                    messagebox.showwarning("Image Error", f"Could not copy image. Using default.\n{e}")
                    db_image_path = 'the.jpg'
            else:
                db_image_path = 'the.jpg'
            try:
                cursor = self.connection.cursor()
                query = ("INSERT INTO movies (title, genre, duration, rating, image_path, description, is_active) "
                         "VALUES (%s, %s, %s, %s, %s, %s, %s)")
                cursor.execute(query, (title, genre, duration_int, rating, db_image_path, desc, int(is_active)))
                self.connection.commit()
                cursor.close()
                messagebox.showinfo("Success", "Movie added successfully!")
                form_win.destroy()
                self.show_movies()
            except Error as e:
                messagebox.showerror("Database Error", f"Error adding movie: {e}")

        Button(form_win, text="Save Movie", command=save, bg=self.highlight_color, fg="white").pack(pady=20)

    def show_edit_movie_form(self, movie):
        form_win = Toplevel(self.root)
        form_win.title("Edit Movie")
        form_win.geometry("400x550")
        form_win.grab_set()

        Label(form_win, text="Title:").pack(anchor=W, padx=20, pady=(20, 0))
        title_entry = Entry(form_win, width=40)
        title_entry.insert(0, movie[1])
        title_entry.pack(padx=20)

        Label(form_win, text="Genre:").pack(anchor=W, padx=20, pady=(10, 0))
        genre_entry = Entry(form_win, width=40)
        genre_entry.insert(0, movie[2])
        genre_entry.pack(padx=20)

        Label(form_win, text="Duration (mins):").pack(anchor=W, padx=20, pady=(10, 0))
        duration_entry = Entry(form_win, width=40)
        duration_entry.insert(0, movie[3])
        duration_entry.pack(padx=20)

        Label(form_win, text="Rating:").pack(anchor=W, padx=20, pady=(10, 0))
        rating_entry = Entry(form_win, width=40)
        rating_entry.insert(0, movie[4])
        rating_entry.pack(padx=20)

        Label(form_win, text="Image Path:").pack(anchor=W, padx=20, pady=(10, 0))
        image_entry = Entry(form_win, width=30)
        image_entry.insert(0, movie[5] if movie[5] else '')
        image_entry.pack(side=LEFT, padx=(20,0))
        def browse_image():
            file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.gif")])
            if file_path:
                image_entry.delete(0, END)
                image_entry.insert(0, file_path)
        browse_btn = Button(form_win, text="Browse", command=browse_image)
        browse_btn.pack(side=LEFT, padx=(5,0))
        Frame(form_win).pack(fill=X)

        Label(form_win, text="Description:").pack(anchor=W, padx=20, pady=(10, 0))
        desc_text = Text(form_win, width=30, height=5)
        desc_text.insert("1.0", movie[6])
        desc_text.pack(padx=20)

        is_active_var = IntVar(value=movie[7])
        Checkbutton(form_win, text="Active", variable=is_active_var).pack(anchor=W, padx=20, pady=(10, 0))

        def update():
            title = title_entry.get()
            genre = genre_entry.get()
            duration = duration_entry.get()
            rating = rating_entry.get()
            image_path = image_entry.get().strip()
            desc = desc_text.get("1.0", "end-1c")
            is_active = is_active_var.get()
            if not title or not genre or not duration or not rating:
                messagebox.showerror("Error", "Please fill all required fields!")
                return
            # Handle image copy and rename by movie title
            if image_path and os.path.exists(image_path):
                try:
                    ext = os.path.splitext(image_path)[1]
                    safe_title = title.strip().replace(' ', '_')
                    import re
                    safe_title = re.sub(r'[^A-Za-z0-9_]', '', safe_title)
                    img_filename = f"{safe_title}{ext}"
                    dest_path = os.path.join("images", img_filename)
                    if not os.path.exists("images"):
                        os.makedirs("images")
                    from shutil import copyfile
                    copyfile(image_path, dest_path)
                    db_image_path = dest_path
                except Exception as e:
                    messagebox.showwarning("Image Error", f"Could not copy image. Using default.\n{e}")
                    db_image_path = 'the.jpg'
            else:
                db_image_path = movie[5] if movie[5] else 'the.jpg'
            try:
                cursor = self.connection.cursor()
                query = ("UPDATE movies SET title=%s, genre=%s, duration=%s, rating=%s, image_path=%s, description=%s, is_active=%s "
                         "WHERE movie_id=%s")
                cursor.execute(query, (title, genre, duration, rating, db_image_path, desc, is_active, movie[0]))
                self.connection.commit()
                messagebox.showinfo("Success", "Movie updated successfully!")
                form_win.destroy()
                self.show_movies()
            except Error as e:
                messagebox.showerror("Database Error", f"Error updating movie: {e}")

        Button(form_win, text="Update Movie", command=update, bg=self.highlight_color, fg="white").pack(pady=20)

    def delete_movie(self, movie_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this movie?"):
            try:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM movies WHERE movie_id=%s", (movie_id,))
                self.connection.commit()
                messagebox.showinfo("Success", "Movie deleted successfully!")
                self.show_movies()
            except Error as e:
                messagebox.showerror("Database Error", f"Error deleting movie: {e}")

    def show_movie_details(self, movie):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Back button
        back_btn = Button(self.content_frame, text="← Back to Movies", font=self.font_small,
                          bg=self.bg_color, fg=self.fg_color, bd=0,
                          command=self.show_movies)
        back_btn.pack(anchor=NW, pady=10)
        
        # Movie details container
        details_frame = Frame(self.content_frame, bg=self.bg_color)
        details_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Left side - Movie poster
        poster_frame = Frame(details_frame, bg=self.bg_color, width=300, height=400)
        poster_frame.pack(side=LEFT, padx=20)
        poster_frame.pack_propagate(False)
        try:
            img_path = movie[5] if movie[5] and os.path.exists(movie[5]) else 'the.jpg'
            img = Image.open(img_path)
            img = img.resize((300, 400), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            poster = Label(poster_frame, image=photo, bg=self.bg_color)
            poster.image = photo
            poster.pack()
        except:
            poster = Label(poster_frame, text="No Image Available", bg=self.bg_color, 
                           fg=self.fg_color, font=self.font_medium)
            poster.pack(expand=True)
        
        # Right side - Movie info and showtimes
        info_frame = Frame(details_frame, bg=self.bg_color)
        info_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Movie title
        title = Label(info_frame, text=movie[1], font=("Helvetica", 24, "bold"),
                      bg=self.bg_color, fg=self.fg_color)
        title.pack(anchor=W, pady=(0, 10))
        
        # Movie details
        details = Label(info_frame, text=f"Genre: {movie[2]}\nDuration: {movie[3]} mins\nRating: {movie[4]}",
                        font=self.font_medium, bg=self.bg_color, fg=self.fg_color, justify=LEFT)
        details.pack(anchor=W, pady=(0, 20))
        
        # Description
        desc = Label(info_frame, text=movie[6], font=self.font_small,
                     bg=self.bg_color, fg=self.fg_color, wraplength=600, justify=LEFT)
        desc.pack(anchor=W, pady=(0, 30))
        
        # Showtimes section
        showtimes_label = Label(info_frame, text="Available Showtimes", font=self.font_large,
                                bg=self.bg_color, fg=self.fg_color)
        showtimes_label.pack(anchor=W, pady=(0, 10))
        
        # Fetch showtimes for this movie
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT s.show_id, s.show_date, s.show_time, s.price, s.available_seats, 
                       sc.screen_name
                FROM showtimes s
                JOIN screens sc ON s.screen_id = sc.screen_id
                WHERE s.movie_id = %s AND s.is_active = TRUE AND s.show_date >= CURDATE()
                ORDER BY s.show_date, s.show_time
            """
            cursor.execute(query, (movie[0],))
            showtimes = cursor.fetchall()
            
            if not showtimes:
                no_showtimes = Label(info_frame, text="No showtimes available for this movie.",
                                    font=self.font_medium, bg=self.bg_color, fg=self.fg_color)
                no_showtimes.pack(anchor=W)
                return
                
            # Create a frame for showtime cards
            showtimes_frame = Frame(info_frame, bg=self.bg_color)
            showtimes_frame.pack(fill=BOTH, expand=True)
            
            for show in showtimes:
                show_card = Frame(showtimes_frame, bg="#34495e", bd=1, relief=SOLID)
                show_card.pack(fill=X, pady=5, padx=5)
                
                # Showtime details
                show_date = datetime.datetime.strptime(str(show[1]), "%Y-%m-%d").strftime("%A, %B %d, %Y")
                show_time = str(show[2])[:-3]  # Remove seconds
                
                details = Label(show_card, 
                               text=f"{show_date} at {show_time}\nScreen: {show[5]} | Price: ${show[3]} | Seats available: {show[4]}",
                               font=self.font_small, bg="#34495e", fg="white", justify=LEFT)
                details.pack(side=LEFT, padx=10, pady=10)
                
                # Book button
                book_btn = Button(show_card, text="Book Now", font=self.font_small,
                                 bg=self.highlight_color, fg="white", bd=0,
                                 command=lambda s=show: self.book_tickets(s, movie))
                book_btn.pack(side=RIGHT, padx=10, pady=10)
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error fetching showtimes: {e}")
    
    def book_tickets(self, showtime, movie):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Back button
        back_btn = Button(self.content_frame, text="← Back to Movie", font=self.font_small,
                          bg=self.bg_color, fg=self.fg_color, bd=0,
                          command=lambda: self.show_movie_details(movie))
        back_btn.pack(anchor=NW, pady=10)
        
        # Booking form container
        booking_frame = Frame(self.content_frame, bg=self.bg_color)
        booking_frame.pack(fill=BOTH, expand=True, padx=50, pady=20)
        
        # Booking header
        show_date = datetime.datetime.strptime(str(showtime[1]), "%Y-%m-%d").strftime("%A, %B %d, %Y")
        show_time = str(showtime[2])[:-3]
        
        header = Label(booking_frame, 
                      text=f"Booking: {movie[1]}\n{show_date} at {show_time} | Screen: {showtime[5]}",
                      font=self.font_large, bg=self.bg_color, fg=self.fg_color)
        header.pack(pady=(0, 20))
        
        # Customer details form
        form_frame = Frame(booking_frame, bg=self.bg_color)
        form_frame.pack(fill=BOTH, expand=True)
        
        # Left side - Customer details
        customer_frame = Frame(form_frame, bg=self.bg_color)
        customer_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=20)
        
        Label(customer_frame, text="Customer Details", font=self.font_medium,
              bg=self.bg_color, fg=self.fg_color).pack(anchor=W, pady=(0, 10))
        
        # Name
        Label(customer_frame, text="Full Name:", font=self.font_small,
              bg=self.bg_color, fg=self.fg_color).pack(anchor=W)
        self.customer_name = Entry(customer_frame, font=self.font_small)
        self.customer_name.pack(fill=X, pady=(0, 10))
        
        # Email
        Label(customer_frame, text="Email:", font=self.font_small,
              bg=self.bg_color, fg=self.fg_color).pack(anchor=W)
        self.customer_email = Entry(customer_frame, font=self.font_small)
        self.customer_email.pack(fill=X, pady=(0, 10))
        
        # Phone
        Label(customer_frame, text="Phone:", font=self.font_small,
              bg=self.bg_color, fg=self.fg_color).pack(anchor=W)
        self.customer_phone = Entry(customer_frame, font=self.font_small)
        self.customer_phone.pack(fill=X, pady=(0, 10))
        
        # Number of tickets
        Label(customer_frame, text="Number of Tickets (1-10):", font=self.font_small,
              bg=self.bg_color, fg=self.fg_color).pack(anchor=W)
        self.num_tickets = Spinbox(customer_frame, from_=1, to=min(10, showtime[4]), 
                                  font=self.font_small)
        self.num_tickets.pack(fill=X, pady=(0, 20))
        
        # Right side - Seat selection (simplified for this example)
        seat_frame = Frame(form_frame, bg=self.bg_color)
        seat_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=20)
        
        Label(seat_frame, text="Seat Selection", font=self.font_medium,
              bg=self.bg_color, fg=self.fg_color).pack(anchor=W, pady=(0, 10))
        
        # Simple seat selection (in a real app, this would be a visual seat map)
        Label(seat_frame, text=f"Select {self.num_tickets.get()} seats (e.g., A1, A2, etc.)", 
              font=self.font_small, bg=self.bg_color, fg=self.fg_color).pack(anchor=W)
        
        self.seat_entries = []
        for i in range(int(self.num_tickets.get())):
            seat_entry = Entry(seat_frame, font=self.font_small)
            seat_entry.pack(fill=X, pady=(0, 5))
            self.seat_entries.append(seat_entry)
        
        # Total price
        total = float(showtime[3]) * int(self.num_tickets.get())
        self.total_label = Label(seat_frame, 
                                text=f"Total: ${total:.2f}",
                                font=self.font_medium, bg=self.bg_color, fg=self.accent_color)
        self.total_label.pack(anchor=W, pady=(20, 0))
        
        # Confirm booking button
        confirm_btn = Button(booking_frame, text="Confirm Booking", font=self.font_medium,
                            bg=self.accent_color, fg="white", bd=0,
                            command=lambda: self.process_booking(showtime, movie, total))
        confirm_btn.pack(pady=(20, 0))
    
    def process_booking(self, showtime, movie, total):
        # Validate inputs
        if not self.customer_name.get():
            messagebox.showerror("Error", "Please enter your name")
            return
            
        if not all(entry.get() for entry in self.seat_entries):
            messagebox.showerror("Error", "Please enter all seat numbers")
            return
            
        try:
            cursor = self.connection.cursor()
            
            # Start transaction
            self.connection.start_transaction()
            
            # 1. Create booking record
            query = """
                INSERT INTO bookings (show_id, customer_name, customer_email, customer_phone, 
                                     num_tickets, total_amount)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                showtime[0],
                self.customer_name.get(),
                self.customer_email.get(),
                self.customer_phone.get(),
                self.num_tickets.get(),
                total
            )
            cursor.execute(query, values)
            booking_id = cursor.lastrowid
            
            # 2. Add seat records
            for seat_entry in self.seat_entries:
                query = "INSERT INTO seats (booking_id, seat_number) VALUES (%s, %s)"
                cursor.execute(query, (booking_id, seat_entry.get()))
            
            # 3. Update available seats in showtime
            query = "UPDATE showtimes SET available_seats = available_seats - %s WHERE show_id = %s"
            cursor.execute(query, (self.num_tickets.get(), showtime[0]))
            
            # Commit transaction
            self.connection.commit()
            
            # Show success message
            messagebox.showinfo("Success", 
                              f"Booking confirmed!\nYour booking ID is: {booking_id}\nTotal: ${total:.2f}")
            
            # Show booking details
            self.show_booking_details(booking_id)
            
        except Error as e:
            self.connection.rollback()
            messagebox.showerror("Database Error", f"Error processing booking: {e}")
    
    def show_booking_details(self, booking_id):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Fetch booking details
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Get booking info
            query = """
                SELECT b.*, m.title, s.show_date, s.show_time, sc.screen_name
                FROM bookings b
                JOIN showtimes s ON b.show_id = s.show_id
                JOIN movies m ON s.movie_id = m.movie_id
                JOIN screens sc ON s.screen_id = sc.screen_id
                WHERE b.booking_id = %s
            """
            cursor.execute(query, (booking_id,))
            booking = cursor.fetchone()
            
            # Get seats
            query = "SELECT seat_number FROM seats WHERE booking_id = %s"
            cursor.execute(query, (booking_id,))
            seats = cursor.fetchall()
            seat_numbers = ", ".join([seat['seat_number'] for seat in seats])
            
            # Booking details container
            details_frame = Frame(self.content_frame, bg=self.bg_color)
            details_frame.pack(fill=BOTH, expand=True, padx=50, pady=20)
            
            # Booking header
            header = Label(details_frame, 
                          text=f"Booking Confirmation - #{booking_id}",
                          font=("Helvetica", 20, "bold"),
                          bg=self.bg_color, fg=self.fg_color)
            header.pack(pady=(0, 20))
            
            # Booking info
            info_frame = Frame(details_frame, bg="#34495e", bd=1, relief=SOLID)
            info_frame.pack(fill=X, pady=10, padx=50)
            
            show_date = booking['show_date'].strftime("%A, %B %d, %Y")
            show_time = str(booking['show_time'])[:-3]
            
            info_text = f"""
Movie: {booking['title']}

Date: {show_date}
Time: {show_time}
Screen: {booking['screen_name']}

Customer: {booking['customer_name']}
Email: {booking['customer_email']}
Phone: {booking['customer_phone']}

Seats: {seat_numbers}
Number of Tickets: {booking['num_tickets']}
Total Amount: ${booking['total_amount']:.2f}

Booking Time: {booking['booking_time']}
            """
            
            info_label = Label(info_frame, text=info_text, font=self.font_medium,
                              bg="#34495e", fg="white", justify=LEFT)
            info_label.pack(padx=20, pady=20)
            
            # Print button (would connect to a printer in a real app)
            print_btn = Button(details_frame, text="Print Ticket", font=self.font_medium,
                              bg=self.highlight_color, fg="white", bd=0)
            print_btn.pack(pady=(20, 0))
            
            # Home button
            home_btn = Button(details_frame, text="Back to Movies", font=self.font_medium,
                             bg=self.accent_color, fg="white", bd=0,
                             command=self.show_movies)
            home_btn.pack(pady=(20, 0))
            
        except Error as e:
            messagebox.showerror("Database Error", f"Error fetching booking details: {e}")
    
    def show_my_bookings(self):
        # Reset buttons
        self.movies_btn.config(bg=self.bg_color)
        self.bookings_btn.config(bg=self.highlight_color)
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Title
        title = Label(self.content_frame, text="My Bookings", font=self.font_large,
                      bg=self.bg_color, fg=self.fg_color)
        title.pack(pady=10)
        
        # Search form
        search_frame = Frame(self.content_frame, bg=self.bg_color)
        search_frame.pack(fill=X, padx=50, pady=10)
        
        Label(search_frame, text="Enter your email or phone number to view bookings:",
              font=self.font_small, bg=self.bg_color, fg=self.fg_color).pack(side=LEFT, padx=(0, 10))
        
        self.search_entry = Entry(search_frame, font=self.font_small, width=30)
        self.search_entry.pack(side=LEFT, padx=(0, 10))
        
        search_btn = Button(search_frame, text="Search", font=self.font_small,
                            bg=self.highlight_color, fg="white", bd=0,
                            command=self.search_bookings)
        search_btn.pack(side=LEFT)
        
        # Results frame
        self.results_frame = Frame(self.content_frame, bg=self.bg_color)
        self.results_frame.pack(fill=BOTH, expand=True, padx=50, pady=10)
        
    def search_bookings(self):
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            messagebox.showerror("Error", "Please enter your email or phone number")
            return
            
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT b.booking_id, b.booking_time, b.num_tickets, b.total_amount,
                       m.title, s.show_date, s.show_time
                FROM bookings b
                JOIN showtimes s ON b.show_id = s.show_id
                JOIN movies m ON s.movie_id = m.movie_id
                WHERE b.customer_email = %s OR b.customer_phone = %s
                ORDER BY b.booking_time DESC
            """
            cursor.execute(query, (search_term, search_term))
            bookings = cursor.fetchall()
            
            if not bookings:
                no_results = Label(self.results_frame, 
                                  text="No bookings found for this email/phone number.",
                                  font=self.font_medium, bg=self.bg_color, fg=self.fg_color)
                no_results.pack(pady=50)
                return
                
            # Display bookings in a list
            for booking in bookings:
                booking_card = Frame(self.results_frame, bg="#34495e", bd=1, relief=SOLID)
                booking_card.pack(fill=X, pady=5)
                
                show_date = booking['show_date'].strftime("%b %d, %Y")
                show_time = str(booking['show_time'])[:-3]
                booking_time = booking['booking_time'].strftime("%b %d, %Y %I:%M %p")
                
                info_text = f"""
Booking #{booking['booking_id']} - {booking_time}
Movie: {booking['title']} | Date: {show_date} {show_time}
Tickets: {booking['num_tickets']} | Total: ${booking['total_amount']:.2f}
                """
                
                info_label = Label(booking_card, text=info_text, font=self.font_small,
                                  bg="#34495e", fg="white", justify=LEFT)
                info_label.pack(side=LEFT, padx=10, pady=10)
                
                view_btn = Button(booking_card, text="View Details", font=self.font_small,
                                  bg=self.highlight_color, fg="white", bd=0,
                                  command=lambda b=booking['booking_id']: self.show_booking_details(b))
                view_btn.pack(side=RIGHT, padx=10, pady=10)
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error searching bookings: {e}")

# Run the application
if __name__ == "__main__":
    root = Tk()
    app = MovieBookingSystem(root)
    root.mainloop()