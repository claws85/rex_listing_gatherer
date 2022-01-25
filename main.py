
import datetime
import logging
import requests
import smtplib
import ssl

from bs4 import BeautifulSoup
from config import (
    ACCOUNT,
    FILE,
    MAIL_SERVER,
    PASSWORD,
    PORT,
    RECIPIENTS,
    TEMPLATE,
    URL
)

logging.basicConfig(filename='rex_listing_gatherer.log', level=logging.INFO)


def main():
    try:
        scraper = DataScraper()
        scraper.run_process()

    except Exception as e:
        logging.error(e)


class DataScraper(object):

    def __init__(self):
        self.url = URL

        self.email_string = TEMPLATE

    def get_soup(self):
        page = requests.get(self.url)
        return BeautifulSoup(page.text, 'html.parser')

    def get_all_listing_data(self):
        soup = self.get_soup()
        return soup.find_all("div", {'class': 'filmsSection'})

    def have_listings_changed(self, listings):
        existing_listings = open(FILE)
        if str(listings) == existing_listings.read():
            return False
        return True

    @staticmethod
    def update_listings_file(listings):
        with open(FILE, 'w') as f:
            f.write(str(listings))

    @staticmethod
    def create_listing_email_text(listing):
        text = '\n\n' + str(listing.find('a').contents[0])
        times = listing.find_all('div', {'class': 'filmsDateDay'})
        for time in times:
            text += '\n    ' + str(time.contents[0])

        return text

    def send_email(self):
        # Create secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(MAIL_SERVER, PORT, context=context) as server:
            server.login(ACCOUNT, PASSWORD)
            email_sent_result = server.sendmail(
                ACCOUNT,
                RECIPIENTS,
                self.email_string.encode('utf-8')
            )

            dt = datetime.datetime.now().strftime("%x %X")
            if not email_sent_result:
                logging.info(
                    "Email sent to recipients successfully at {}.\n".format(dt)
                )

    def run_process(self):

        listed_films = self.get_all_listing_data()

        if self.have_listings_changed(listed_films):

            for listing in listed_films:
                text = self.create_listing_email_text(listing)
                self.email_string += text

            self.send_email()

            self.update_listings_file(listed_films)


if __name__ == "__main__":
    main()
