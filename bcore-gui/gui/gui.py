import time
import functools
import pprint

#lint:disable
from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.actionbar import ActionBar
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch

from kivy.properties import (ListProperty,
                            StringProperty,
                            ObjectProperty,
                            DictProperty)
from kivy.clock import Clock
from kivy.config import Config
from kivy.garden.datetimepicker import DatePicker, TimePicker
from kivy.graphics.vertex_instructions import (Rectangle,
                                               Ellipse,
                                               Line)
from kivy.graphics.context_instructions import Color

from bcore.classes.Subject import Subject, Mouse, Rat, VirtualSubject, Human, DefaultMouse, DefaultRat, DefaultVirtual, DefaultHuman
#lint:enable


###############################################################################
#                                OTHERS                                       #
###############################################################################

class HelpText(Label):
    pass


class StatusLabel(Label):
    Status = StringProperty('ALLOK')
    ux_ALLOK = [0.56, 0.93, 0.56, 0.5]
    ux_ERROR = [0.93, 0.56, 0.56, 0.5]
    ux_CONCERN = [0.99, 0.56, 0., 0.5]

    StatusColorDict = DictProperty({
        'ALLOK': ux_ALLOK,
        'ERROR': ux_ERROR,
        'CONCERN': ux_CONCERN
        })

    def on_Status(self, instrFrom, value):
        with self.canvas:
            try:
                Color(self.StatusColorDict[value], mode='rgba')
            except KeyError:
                Color(self.StatusColorDict['ERROR'], mode='rgba')
                self.text = self.text + '\nUnknown status!'


class StationButton(Button):
    ux_LIGHTGREENCOLOR = [0.56, 0.93, 0.56, 0.75]
    ux_LIGHTREDCOLOR = [0.93, 0.56, 0.56, 0.75]


class SubjectIDInput(TextInput):
    def validate_subID_input(self, call):
        for c in self.text:
            if c in (' ', '-'):
                self.text = 'Only alphanumerics and underscores allowed'

    def get_text(self):
        return self.text

class ChoiceSpinner(Spinner):
    def get_text(self):
        return self.text
###############################################################################
#                                ACTION BARS                                  #
###############################################################################
class BaseActionBar(ActionBar):
    pass


class SubjectControlActionBar(ActionBar):
    pass


class StationControlActionBar(ActionBar):
    pass


class SubjectStatsActionBar(ActionBar):
    pass


class StationStatsActionBar(ActionBar):
    pass


###############################################################################
#                                SCREENS                                      #
###############################################################################
class BServerAppScreenManager(ScreenManager):
    pass


class BaseScreen(Screen):
    def update_screen(self, data):
        self.update_subjects(data.get_subject_ids())
        # allow scroll
        self.enable_scroll()
        self.update_stations(data.get_station_names())

    def enable_scroll(self):
        subject_list = self.ids['subject_listing']
        subject_list.bind(minimum_height=subject_list.setter('height'))

    def update_subjects(self, subjects):
        subject_list = self.ids['subject_listing']
        for subject in subjects:
            subjLbl = StatusLabel(text='Subject_' + subject,
                height=30,
                size_hint_y=None)
            subject_list.add_widget(subjLbl)

    def update_stations(self, stations):
        station_list = self.ids['station_listing']
        for station in stations:
            stLbl = StatusLabel(text='Station:\n' + station,
                )
            station_list.add_widget(stLbl)


class SubjectStatisticsScreen(Screen):
    def update_screen(self, data):
        self.update_subjects(data.get_subject_ids())
        # allow scroll
        self.enable_scroll()

    def update_subjects(self, subjects):
        subject_list = self.ids['subject_button_listing']
        for subject in subjects:
            subjLbl = Button(text='Subject_' + subject,
                height=30,
                size_hint_y=None)
            subject_list.add_widget(subjLbl)

    def enable_scroll(self):
        subject_list = self.ids['subject_button_listing']
        subject_list.bind(minimum_height=subject_list.setter('height'))


class StationStatisticsScreen(Screen):
    def update_screen(self, data):
        self.update_stations(data.get_station_names())
        self.enable_scroll()

    def enable_scroll(self):
        subject_list = self.ids['station_button_listing']
        subject_list.bind(minimum_height=subject_list.setter('height'))

    def update_stations(self, stations):
        station_list = self.ids['station_button_listing']
        for station in stations:
            stLbl = Button(text='Station:\n' + station,
                )
            station_list.add_widget(stLbl)


class AddSubjectScreen(Screen):
    def extract_data_and_add_subject(self, kw_function, example, app,
        pressedButton):
        print('creating values and adding subjects')
        kw_value = {}
        for key, value in kw_function.items():
            if hasattr(value, '__call__'):
                kw_value[key] = value()
            else:
                kw_value[key] = value
            print (key, kw_value[key])
        app.serverData.add_subject(example.create_subject(**kw_value))

    def present_species_specific_widgets(self, layout, present, details,
        example, app):
        kw_function = {}
        # now add a vertical box layout and add the choices
        OtherFields = BoxLayout(spacing=3, orientation='vertical')
        # subjectID
        if present['subjectID']:
            subjectIDLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            subjectIDLayout.add_widget(Label(text='Subject ID'))
            subIDInput = SubjectIDInput(hint_text='Press Enter when done',
                multiline=False)
            subIDInput.bind(on_text_validate=subIDInput.validate_subID_input)
            subjectIDLayout.add_widget(subIDInput)
            OtherFields.add_widget(subjectIDLayout)
            kw_function['subjectID'] = subIDInput.get_text

        # firstName
        if present['firstName']:
            FirstNameLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            FirstNameLayout.add_widget(Label(text='First Name'))
            firstNameInput = SubjectIDInput(hint_text='First',
                multiline=False)
            FirstNameLayout.add_widget(firstNameInput)
            OtherFields.add_widget(FirstNameLayout)
            kw_function['firstName'] = firstNameInput.get_text

        # lastName
        if present['lastName']:
            LastNameLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            LastNameLayout.add_widget(Label(text='Last Name'))
            lastNameInput = SubjectIDInput(hint_text='Last',
                multiline=False)
            LastNameLayout.add_widget(lastNameInput)
            OtherFields.add_widget(LastNameLayout)
            kw_function['lastName'] = lastNameInput.get_text

        # gender
        if present['gender']:
            genderLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            genderLayout.add_widget(Label(text='Sex'))
            genderInput = ChoiceSpinner(text=details['allowedGenders'][0],
                values=details['allowedGenders'],
                size=(150, 40))
            genderLayout.add_widget(genderInput)
            OtherFields.add_widget(genderLayout)
            kw_function['gender'] = genderInput.get_text

        # dob
        if present['dob']:
            dobLayout = BoxLayout(orientation='horizontal', height=88,
                size_hint_y=None)
            dobLayout.add_widget(Label(text='Date of Birth'))
            dobInput = DatePicker()
            dobLayout.add_widget(dobInput)
            OtherFields.add_widget(dobLayout)
            kw_function['birthDate'] = dobInput.get_datetime

        # strains
        if present['strains']:
            strainLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            strainLayout.add_widget(Label(text='Strain'))
            strainInput = ChoiceSpinner(text=details['allowedStrains'][0],
                values=details['allowedStrains'],
                size=(150, 40))
            strainLayout.add_widget(strainInput)
            OtherFields.add_widget(strainLayout)
            kw_function['strain'] = strainInput.get_text

        # geneBkgd
        if present['geneBkgd']:
            geneBkgdLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            geneBkgdLayout.add_widget(Label(text='Genetic Background'))
            geneBkgdInput = ChoiceSpinner(text=details['allowedGeneBkgd'][0],
                values=details['allowedGeneBkgd'],
                size=(150, 40))
            geneBkgdLayout.add_widget(geneBkgdInput)
            OtherFields.add_widget(geneBkgdLayout)
            kw_function['geneBkgd'] = geneBkgdInput.get_text

        # anonymize
        if present['anonymize']:
            anonLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            anonLayout.add_widget(Label(text='Anonymize'))
            anonInput = Switch(active=False)
            anonLayout.add_widget(anonInput)
            OtherFields.add_widget(anonLayout)
            kw_function['anonymize'] = anonInput.active

        print ('[INFO]\t added species specific widgets')
        largeBlankSpace = BoxLayout(orientation='horizontal', height=80,
                size_hint_y=None)
        OtherFields.add_widget(largeBlankSpace)
        print ('[INFO]\t added blank space')
        addSubjectLayout = BoxLayout(orientation='horizontal', height=80,
                size_hint_y=None)
        addSubjectButton = Button(text='Add Subject')
        extract_data_and_add_subject = functools.partial(
            self.extract_data_and_add_subject, kw_function, example, app)
        addSubjectButton.bind(on_press=extract_data_and_add_subject)
        addSubjectLayout.add_widget(addSubjectButton)
        OtherFields.add_widget(addSubjectLayout)
        print ('[INFO]\t added add subject button')
        layout.add_widget(OtherFields)

    def updateSpeciesSpecificChoice(self, species, layout, app):
        # if there are any old widgets to the layout, clear it
        layout.clear_widgets()
        present = {
            'subjectID': False,
            'firstName': False,
            'lastName': False,
            'gender': False,
            'dob': False,
            'strains': False,
            'geneBkgd': False,
            'anonymize': False
            }
        details = {}
        if species == 'Mouse':
            example = DefaultMouse()
            details['allowedGenders'] = example.allowed_genders()
            details['allowedStrains'] = example.allowed_strains()
            details['allowedGeneBkgd'] = example.allowed_gene_bkgd()
            present['subjectID'] = True
            present['gender'] = True
            present['dob'] = True
            present['strains'] = True
            present['geneBkgd'] = True

            self.present_species_specific_widgets(
                layout, present, details, example, app)
        elif species == 'Rat':
            example = DefaultRat()
            details['allowedGenders'] = example.allowed_genders()
            details['allowedStrains'] = example.allowed_strains()
            details['allowedGeneBkgd'] = example.allowed_gene_bkgd()
            present['subjectID'] = True
            present['gender'] = True
            present['dob'] = True
            present['strains'] = True
            present['geneBkgd'] = True

            self.present_species_specific_widgets(
                layout, present, details, example, app)
        elif species == 'Virtual':
            example = DefaultVirtual()
            present['subjectID'] = True

            self.present_species_specific_widgets(
                layout, present, details, example, app)
        elif species == 'Human':
            example = DefaultHuman()
            details['allowedGenders'] = example.allowed_genders()
            present['firstName'] = True
            present['lastName'] = True
            present['gender'] = True
            present['dob'] = True
            present['anonymize'] = True

            self.present_species_specific_widgets(
                layout, present, details, example, app)

###############################################################################
#                                ROOT WIDGET                                  #
###############################################################################
class BServerWidget(BoxLayout):

    def changeToSubjectStatisticsScreen(self, data):
        print ('changing to subject statistics')
        screenMgr = self.ids['screen_manager']
        self.ids['subject_statistics'].update_screen(data)
        screenMgr.current = 'SubjectStatistics'

    def changeToStationStatisticsScreen(self, data):
        print ('changing to station statistics')
        screenMgr = self.ids['screen_manager']
        self.ids['station_statistics'].update_screen(data)
        screenMgr.current = 'StationStatistics'

    def changeToAddSubjectScreen(self, data):
        print ('changing to add subject')
        screenMgr = self.ids['screen_manager']
        screenMgr.current = 'AddSubject'

    def changeToBaseScreen(self, data):
        print ('changing to base screen')
        screenMgr = self.ids['screen_manager']
        self.ids['base_screen'].update_screen(data)
        screenMgr.current = 'BaseScreen'

    def changeScreen(self, screen, data):
        if screen == 'SubjectStatistics':
            self.changeToSubjectStatisticsScreen(data)
        elif screen == 'StationStatistics':
            self.changeToStationStatisticsScreen(data)
        elif screen == 'AddSubject':
            self.changeToAddSubjectScreen(data)
        elif screen == 'BaseScreen':
            self.changeToBaseScreen(data)

###############################################################################
#                                APP                                          #
###############################################################################
class BServerApp(App):
    # these are basic app-level data structures
    Subjects = ListProperty()
    Stations = ListProperty()
    Assignments = ListProperty()
    serverData = ObjectProperty()
    DefaultSubjects = ListProperty(['sub1', 'sub2'])
    DefaultStations = ListProperty(['stn1', 'stn2', 'stn3',
        'stn4', 'stn5', 'stn6'])
    cache = ListProperty()
    ux_CurrTime = StringProperty(time.strftime('%H::%M::%S'))

    def updateTime(self, dt):
        self.ux_CurrTime = time.strftime('%H::%M::%S')

    def build(self, *args):
        # get the server data imported
        self.serverData = self.options['serverData']
        # create widget
        self.widget = bserver_widget = BServerWidget()
        Clock.schedule_interval(self.updateTime, 1)
        # start at the base screen
        self.changeScreen('BaseScreen')

        return bserver_widget

    def changeScreen(self, screen):
        self.widget.changeScreen(screen, data=self.serverData)


if __name__ == "__main__":
    from bcore.classes.ClientAndServer.BServer import BServerLocal
    Config.set('graphics', 'fullscreen', 'fake-fullscreen')
    Config.write()
    app = BServerApp(serverData=BServerLocal()).run()
    Config.set('graphics', 'fullscreen', 0)
    Config.write()