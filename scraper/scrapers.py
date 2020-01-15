"""
Scrapers
    Scraper class objects to wrap functionality
"""
import numpy as np
from write_query import (filter_unique, write_business_search, write_search_metadata,
                            write_categories)
import lens
from paths import SpiralPath
from app_global import g

from scraper_1_urls import geo_search

from scraper_1_reviews import review_search, save_reviews

import logging
scraper_logger = logging.getLogger(__name__)


class Scraper():
    def __init__(self):
        self.logger = scraper_logger
        self.logger.info("Creating Scraper")
        self.working_item = None
        self.complete = []
        self.failed = []
    def run(self):
        NotImplemented
    def move(self):
        NotImplemented
    def search(self):
        NotImplemented
    def save(self):
        NotImplemented
    def stop(self):
        NotImplemented


class GeoScraper(Scraper):
    """
    GeoScraper
        Geographically aware scraper implementing Lens for smart pathing
    """
    def __init__(self, start_coord, radius, category, expected_max=50):
        self.coordinates = start_coord
        self.max_radius = radius
        self.category = category
        self.path = SpiralPath(center_coord=start_coord, max_radius=radius)
        self.stopping_param = 0
        self.stopped=False
        self.expected_max = expected_max
        super().__init__()

    def run(self):
        # Loop through hops until the end of path is reached
        while not self.stopped:
            continue # search, move, search,.
        pass

    def move(self, d_theta=np.pi/12, c=0.025):
        # Calculate expected value for d_theta and adjust curvature
        magnitude = modelmap.predict_capture()/self.expected_max
        # TODO: The path parameters can be set with general params instead of explicitly with a little work.
        self.coordinates = selp.path.move(d_theta=d_theta, c=c, magnitude=magnitude)
    
    def search(self):
        results = geo_search(
            category=self.category,
            latitude=self.coordinates[0],
            longitude=self.coordinates[1]
            )
        unique_results = filter_unique(results)
        self.save(
            unique_results=unique_results,
        )
        # self.move()

    def save(self, unique_results):
        # Save new businesses
        write_business_search(unique_frame=unique_results)
        # Save search results metadata
        search_record = {
            'latitude': self.coordinates[0],
            'longitude': self.coordinates[1],
            'category': self.category,
            'num_unique': len(unique_results),
        }
        write_search_metadata(record=search_record)
        self.stop(num_unique=len(unique_results))

    def stop(self, *args, **kwargs):
        if kwargs['num_unique'] == 0:
            self.stopping_param += 1

        if self.stopping_param > 5:
            self.stopped=True


class ListScraper(Scraper):
    """
    ListScraper
        Natively multithreaded scraper to return multiple requests given a
        list of search strings and appropriate search function.
    """
    def __init__(self, search_list: list):
        self.search_list = search_list
        super().__init__()

    def run(self):
        self.working_item = self.move()  # Initialize first search item
        while self.working_item:  # Start loop through list
            try:
                self.search()
                self.complete.append(self.working_item)
                self.working_item = self.move()
            except:
                self.failed.append(self.working_item)
                self.logger.error('Search Failed on: '.foromat(self.working_item))
        self.logger.info('List Scraper Run Complete.  {} Complete. {} Failed.'.format(
            len(self.complete), len(self.failed)))
        return True

    def search(self):
        response = review_search(self.working_item)
        self.save(response)

    def move(self):
        # pop url, store popped temporarily in working.
        if len(self.search_list) > 0:
            return self.search_list.pop()
        else:
            return False

    def save(self, reviews_to_save: list):
        save_reviews(reviews_to_save)


########################
### Helper Functions ###
########################

# GeoScraper Local Functions #

def calc_a_max(max_radius):
    a_max = [np.log(max_radius) / theta for theta in np.linspace(0.001, 2*np.pi, 12)]
    a_max = min(a_max)/10
    return a_max


def get_decimal_from_polar(center_coord, r, theta, a):
    def get_offset(theta, a):
        r = np.exp(-a*theta)
        lat = r * np.sin(theta)
        lon = r * np.cos(theta)
        return(lat,lon)
    offset = get_offset(theta, a)
    return (center_coord[0]+offset[0], center_coord[1]+offset[1])


def create_geo_scraper(city, radius, category, coordinates = None):
    """
    Create a geographic yelp scraper for businesses. 
    """

    if city is not None:
        coordinates = lookup_city_coordinates(city)
    elif coordinates is None:
        scraper_logger.error('City or Coordinates invalid')
        raise ValueError('City and coordinates not provided')
    
    return GeoScraper(
        start_coord=coordinates,
        radius=radius,
        category=category
    )

def points_along_path(steps=12, **kwargs):
    # Spiral conversion
    # Convert rotation to steps of lon, lat

def predict_capture():
    pass


# ListScraper Functions #
    # Might be able to move try/accept run statement out to some extent.  Not critical yet.