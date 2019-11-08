import logging
from datetime import datetime
from models import *


query_logger = logging.getLogger(__name__)

class Query():
    def __init__(self, session, query):
        self.session = session
        self.query = query

    def check_constraints(self, record):
        """Check for constraints in a record.
            If any found, create empty rows with needed keys to enforce relational constraints.
            Also handle known typing difficulties with SQL Alchemy (datetime)
        """
        # DateTime Checks
        query_logger.info('Checking for datetime fields')
        for field in ['date', 'yelping_since']:
            if field in record.keys():
                record[field] = convert_to_datetime(record[field])

        # Foreign Key Checks
        if 'business_id' in record.keys():
            query_logger.info('business_id found in query.  Checking for existing record.')
            exists = self.session.query(Business).filter_by(business_id=record['business_id']).scalar() is not None
            if not exists:
                query_logger.info('business_id did not return existing row. Generating empty row.')
                business = Business(business_id=record['business_id'])
                self.session.add(business)

        if 'user_id' in record.keys():
            query_logger.info('user_id found in query.  Checking for existing record.')
            exists = self.session.query(User).filter_by(user_id=record['user_id']).scalar() is not None
            if not exists:
                query_logger.info('user_id did not return existing row. Generating empty row.')
                user = User(user_id=record['user_id'])
                self.session.add(user)

        self.session.commit()

    def fill(self, data):
        NotImplemented

    def execute(self):
        NotImplemented


class Get(Query):
    def __init__(self, session, query):
        super().__init__(session, query)
        query_logger.info('GET query created.')
        self.contents_ = None  # Generate from execution step


class Post(Query):
    def __init__(self, session, query):
        super().__init__(session, query)
        query_logger.info('POST query created')
        query_logger.debug('Session: {} Query: {}'.format(session, query))
        self.query = query
        self.maker = assign_maker(query['table_name'])
        self.fill(query['data'])


    def fill(self, records):
        assert type(records) == list
        query_logger.info('Adding {} records to session stack.'.format(len(records)))
        for record in records:
            self.check_constraints(record)
            self.maker(self.session, record)

    def execute(self):
        self.session.commit()


###################
###Query Methods###
###################

def convert_to_datetime(time_string):
    query_logger.info('Converting {} to datetime'.format(time_string))
    try:
        assert type(time_string) == str
        return datetime.fromisoformat(time_string)
    except ValueError:
        query_logger.info('Value Error: Invalid isoformat string')
        query_logger.info('Sending default datetime')
        return datetime.fromisoformat('1969-01-01')
    except AssertionError:
        query_logger.info('AssertionError: DateTime not a string.')
        query_logger.info('Attempting translation')
        return datetime.fromtimestamp(time_string / 1e3)
    except:
        raise


###########################
###Make Instance Methods###
###########################
# TODO: Collapse into single makre factory that calls proper class
def assign_maker(table_name):
    makers = {
        'businesses': make_or_update_business,
        'users': make_or_update_user,
        'checkins': make_or_update_checkin,
        'photos': make_or_update_photo,
        'tips': make_or_update_tip,
        'reviews': make_or_update_review,
    }
    return makers[table_name]


def make_or_update_business(session, record, *args, **kwargs):
    # Check if existing to UPDATE or INSERT
    exists = session.query(Business).filter_by(business_id=record['business_id']).scalar() is not None
    if not exists:
        query_logger.info('business_id did not return existing row. Creating new business instance')
        session.add(Business(**record))
    else:
        session.query(Business).filter_by(business_id=record['business_id']).update(record)


def make_or_update_user(session, record, *args, **kwargs):
    # Check if existing to UPDATE or INSERT
    exists = session.query(User).filter_by(user_id=record['user_id']).scalar() is not None
    if not exists:
        query_logger.info('user_id did not return existing row. Creating new business instance')
        session.add(User(**record))
    else:
        session.query(User).filter_by(user_id=record['user_id']).update(record)


def make_or_update_checkin(session, record, *args, **kwargs):
    # Check if existing to UPDATE or INSERT
    exists = session.query(Checkin).filter_by(checkin_id=record['checkin_id']).scalar() is not None
    if not exists:
        query_logger.info('checkin_id did not return existing row. Creating new business instance')
        session.add(Checkin(**record))
    else:
        session.query(Checkin).filter_by(checkin_id=record['checkin_id']).update(record)


def make_or_update_photo(session, record, *args, **kwargs):
    # Check if existing to UPDATE or INSERT
    exists = session.query(Photo).filter_by(photo_id=record['photo_id']).scalar() is not None
    if not exists:
        query_logger.info('photo_id did not return existing row. Creating new business instance')
        session.add(Photo(**record))
    else:
        session.query(Photo).filter_by(photo_id=record['photo_id']).update(record)


def make_or_update_tip(session, record, *args, **kwargs):
    # Check if existing to UPDATE or INSERT
    exists = session.query(Tip).filter_by(tip_id=record['tip_id']).scalar() is not None
    if not exists:
        query_logger.info('tip_id did not return existing row. Creating new business instance')
        session.add(Tip(**record))
    else:
        session.query(Tip).filter_by(tip_id=record['tip_id']).update(record)


def make_or_update_review(session, record, *args, **kwargs):
    # Check if existing to UPDATE or INSERT
    exists = session.query(Review).filter_by(review_id=record['review_id']).scalar() is not None
    if not exists:
        query_logger.info('review_id did not return existing row. Creating new business instance')
        session.add(Review(**record))
    else:
        session.query(Review).filter_by(review_id=record['review_id']).update(record)