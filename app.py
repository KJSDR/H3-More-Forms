from flask import Flask, request, render_template
from PIL import Image, ImageFilter
from dotenv import load_dotenv
import os
import random
import requests
import json
from pprint import PrettyPrinter  


load_dotenv()


app = Flask(__name__)


pp = PrettyPrinter(indent=4)


list_of_compliments = [
    'awesome', 'beatific', 'blithesome', 'conscientious', 'coruscant', 'erudite',
    'exquisite', 'fabulous', 'fantastic', 'gorgeous', 'indubitable', 'ineffable',
    'magnificent', 'outstanding', 'propitioius', 'remarkable', 'spectacular', 
    'splendiferous', 'stupendous', 'super', 'upbeat', 'wondrous', 'zoetic'
]

@app.route('/')
def homepage():
    """A homepage with handy links for your convenience."""
    return render_template('home.html')


################################################################################
# COMPLIMENTS ROUTES
################################################################################

@app.route('/compliments')
def compliments():
    """Shows the user a form to get compliments."""
    return render_template('compliments_form.html')

@app.route('/compliments_results', methods=['GET'])
def compliments_results():
    """Show the user some compliments."""
    
    
    users_name = request.args.get('users_name')
    wants_compliments = request.args.get('wants_compliments')
    num_compliments = request.args.get('num_compliments', type=int)

    
    if wants_compliments == 'yes' and num_compliments:
        compliments_to_show = random.sample(list_of_compliments, num_compliments)
    else:
        compliments_to_show = []

    
    context = {
        'name': users_name,  
        'compliments': compliments_to_show  
    }

    return render_template('compliments_results.html', **context)




################################################################################
# ANIMAL FACTS ROUTE
################################################################################

animal_to_fact = {
    'koala': 'Koala fingerprints are so close to humans\' that they could taint crime scenes.',
    'parrot': 'Parrots will selflessly help each other out.',
    'mantis shrimp': 'The mantis shrimp has the world\'s fastest punch.',
    'lion': 'Female lions do 90 percent of the hunting.',
    'narwhal': 'Narwhal tusks are really an "inside out" tooth.'
}

@app.route('/animal_facts')
def animal_facts():
    """Show a form to choose an animal and receive facts."""

    chosen_animal = request.args.get('animal')
    animal_fact = animal_to_fact.get(chosen_animal) if chosen_animal else None

    context = {
        'animals': animal_to_fact.keys(),
        'chosen_animal': chosen_animal,
        'animal_fact': animal_fact
    }

    return render_template('animal_facts.html', **context)


################################################################################
# IMAGE FILTER ROUTE
################################################################################


filter_types_dict = {
    'blur': ImageFilter.BLUR,
    'contour': ImageFilter.CONTOUR,
    'detail': ImageFilter.DETAIL,
    'edge enhance': ImageFilter.EDGE_ENHANCE,
    'emboss': ImageFilter.EMBOSS,
    'sharpen': ImageFilter.SHARPEN,
    'smooth': ImageFilter.SMOOTH
}

def save_image(image, filter_type):
    """Save the image with the filter applied and return the file path."""
    new_file_name = f"{filter_type}-{image.filename}"
    file_path = os.path.join(app.root_path, 'static/images', new_file_name)
    image.save(file_path)
    return file_path

def apply_filter(file_path, filter_name):
    """Apply the selected filter to the image."""
    image = Image.open(file_path)
    image.thumbnail((500, 500))
    image = image.filter(filter_types_dict.get(filter_name))
    image.save(file_path)

@app.route('/image_filter', methods=['GET', 'POST'])
def image_filter():
    """Filter an image uploaded by the user using the Pillow library."""
    filter_types = filter_types_dict.keys()

    if request.method == 'POST':
        filter_type = request.form.get('filter_type')
        image = request.files.get('users_image')

        if image and filter_type:
            file_path = save_image(image, filter_type)
            apply_filter(file_path, filter_type)

            image_url = f'./static/images/{image.filename}'
            context = {
                'filter_types': filter_types,
                'image_url': image_url
            }

            return render_template('image_filter.html', **context)
    
    
    context = {
        'filter_types': filter_types
    }
    return render_template('image_filter.html', **context)


################################################################################
# GIF SEARCH ROUTE
################################################################################

API_KEY = os.getenv('API_KEY')
TENOR_URL = 'https://tenor.googleapis.com/v2/search'

@app.route('/gif_search', methods=['GET', 'POST'])
def gif_search():
    """Show a form to search for GIFs and show resulting GIFs from Tenor API."""
    
    gifs = None  
    error_message = None  
    
    if request.method == 'POST':
        search_query = request.form.get('search_query')  
        quantity = request.form.get('quantity', type=int)  
        
        
        if not search_query:
            error_message = "Please enter a search query."
            return render_template('gif_search.html', error_message=error_message)
        
        
        response = requests.get(
            TENOR_URL,
            params={
                'q': search_query,
                'key': API_KEY,
                'limit': quantity,
            }
        )

        
        if response.status_code == 200:
            gifs = response.json().get('results', [])
        else:
            error_message = "Sorry, there was an issue fetching GIFs. Please try again later."
            return render_template('gif_search.html', error_message=error_message)

    
    return render_template('gif_search.html', gifs=gifs, error_message=error_message)



################################################################################
# Main Entry Point
################################################################################

if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True, port=5001)
