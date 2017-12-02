from selenium.common.exceptions import NoSuchElementException

from .misc import Idable, Findable, find_or_new, \
                  LazyClass, lazyproperty, \
                  find_elements_in_scrollpane, seleniumdriven

def find(_id):
    return find_or_new(Album, _id)

class Album(Idable, Findable, LazyClass):
    BASE = "https://music.yandex.ru/album/{id}"

    def __init__(self, _id, title=None, artist=None, year=None, songs=None):
        self._id = _id
        self._title = title
        self._artist = artist
        self._year = year
        self._songs = songs or list()

    @lazyproperty
    @seleniumdriven()
    def title(self, driver):
        title_el = driver.find_element_by_class_name('page-album__title')
        try:
            title_heading = title_el.find_element_by_tag_name('h1')
        except NoSuchElementException as e:
            title_heading = None
        try:
            title_subheading = title_el.find_element_by_tag_name('span')
        except NoSuchElementException as e:
            title_subheading = None
        titles = []
        if title_heading:
            titles.append(title_heading.text)
        if title_subheading:
            titles.append(title_subheading.text)
        return " ".join(titles)

    @lazyproperty
    @seleniumdriven()
    def artist(self, driver):
        el = driver.find_elements_by_css_selector('.album-summary__large > :first-child a')[0]
        _id = el.get_attribute('href').split('/')[-1]
        title = el.get_attribute('title')
        artist = Artist.find(_id)
        artist.title = title
        return artist

    @lazyproperty
    @seleniumdriven()
    def year(self, driver):
        year = driver.find_elements_by_css_selector('.album-summary__large > :last-child')[0].text
        year = year.split(' ')[0] if year is not None else None
        return year

    @lazyproperty
    @seleniumdriven(prefetch=False)
    def songs(self, driver):
        def process(el):
            def process_trackname(el):
                _id = el.find_element_by_tag_name('a').get_attribute('href').split('/')[-1]
                title = el.text
                song = Song.find(self.id, _id)
                song.title = title
                return song
            def process_trackinfo(el):
                song.duration = el.text
                return song
            song = process_trackname(el.find_element_by_class_name('d-track__name'))
            song = process_trackinfo(el.find_element_by_class_name('typo-track'))
            song.album = self
            return song
        return [process(el) for el in driver.find_elements_by_class_name('d-track')]

    @seleniumdriven()
    def play(self, driver):
        try:
            driver.find_element_by_class_name('page-album__play').click()
        except NoSuchElementException as e:
            print(e)
            return None

    @seleniumdriven()
    def pause(self, driver):
        try:
            driver.find_element_by_css_selector('.page-album__play.button-play_playing').click()
        except NoSuchElementException:
            return None


from .artist import Artist
from .song import Song
