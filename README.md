# Book Recommendation App

<b> Project: </b> Build a recommender system that could update recommendations based on read books stored by user in a database.

I listen to a lot of audiobooks and often find myself seeking out "similar books" as soon as I finish one so I am constantly looking for new books to read. Usually the best recommendations come from my husband, who reads a lot of the same books as I do but I figured I could find more books if I extend that pool of 'similar readers'. A book recommender system seemed a logical first step. 

### Dataset
I started with the <a href = "http://www2.informatik.uni-freiburg.de/~cziegler/BX/"> Book Crossing </a> dataset compiled by Craig Nicolas Ziegler in order to build recommender system. These data include both implicit ratings and explicit ratings. In this case, explicit ratings are actual ratings of books on a scale of 1 - 10 indictated the extent to which the user enjoyed the book. Implict readings are simply 'yes/no'; did this user read this book? While implicit ratings are much easier to gather from users, I choose to base my recommender off of explicit ratings so that it was easier to rank the recommendations from 'most likely to be enjoyed' to 'least likely to be enjoyed'. 

### Model
The recommender was built loosely follwing Chhavi Saluja's <a href = "https://towardsdatascience.com/my-journey-to-building-book-recommendation-system-5ec959c41847" > Book Recommendation System </a> blog. I outline the steps below. 

To reduce the data, I separated the ratings into implicit and explicit ratings. I also deleted any users who only had read books not in the books dataset and removed books not read by any users in the user dataset. To make the most efficient data base, I also compacted books with the same title and author into a single ISBN. This increases the rating count for most books and makes searching the database for specific books much more straight forward. Finally, to reduce the size of the eventual pivot table I also removed books and users with under a minimum number of ratings/books. 

The recommender system makes user of user-based collaborative filtering. For a given user, the 10 most similar users are found with through a k-neighbors algorithm. 100 possible recommendation books are found by looking at the 100 most occuring books within the 10 most similar users. The expected rating is then determined for each of the 100 possible recommendations by weighting each user's rating by their similarity to the base user. The top 10 books with the highest expected ratings are then returned as recommendations. 

The base implementation of the recommender is in <a href = "https://github.com/astrojneil/bookRec/blob/main/BookRecommender.ipynb" > this jupyter notebook</a>, and is implemented for the app in <a href = "https://github.com/astrojneil/bookRec/blob/main/recommender.py" > recommender.py </a>. 

### Database
The easiest way to store the book/rating dataset as well as the information for new users was with an sqlite database. The conversion from the original .csv files to a database is found in <a href="https://github.com/astrojneil/bookRec/blob/main/create_db.py"> create_db.py </a>. This script constructs the tables within the database as well as performs the cleaning described above.

Books and Users are also treated as their own classes in order to optimize the recommend, add and display functions within the app. they are implemented in <a href = "https://github.com/astrojneil/bookRec/blob/main/books.py" > books.py </a> and <a href = "https://github.com/astrojneil/bookRec/blob/main/users.py" > users.py </a> respectively. 

### App
In order to make recommendations for new users, I constructed an app with flask. I adapted the <a href = "https://flask.palletsprojects.com/en/1.1.x/tutorial/factory/" > Flask Blog Post Tutorial </a> to save users' book and ratings to a specific profile and generate a home page that lists recommendations based on the users' stored books. 

### Upcoming Developments
Currently the only books that can be added to a user's profile need to be within the original dataset. An upcoming feature will be to implement a 'add new book' function while will make use of the <a href = "https://www.goodreads.com/api" >Goodreads API </a> to find the author and ISBN of a book given the user's input title. 
