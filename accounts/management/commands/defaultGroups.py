from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

"""
Create permission groups
Create permissions (read only) to models for a set of groups
"""
import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from data.models import PointCodes, PlistCutoff
from configuration.models import Configuration
import datetime

User = get_user_model()

USERS = [
    # ['username', 'first', 'last, 'email', 'password', is_superuser, is_staff, can_view, no_entry, permission groups]
    ['manderson', 'Mason', 'Anderson', 'masonanderson0@gmail.com', '2.718281', True, True, True, False, []],
    ['jchiu', 'Joshua', 'Chiu', 'joshuachiu2020@gmail.com', '2.718281', True, True, True, False, []],
    ['databaseadmin', 'Database', 'Administration', 'pointgreydb@gmail.com', '2.718281', True, True, True, False, []],

    # ['npetheriot', 'Nick', 'Petheriotis', 'npetheriot@vsb.bc.ca', 'wK7CSZVQnv', True, True, True, False, []],
    # ['jdouglas', 'Julie', 'Douglas', '', 'FqkuNHt2Hn', False, False, False, True, ['Athletics', 'Service']],
    # ['dlai', 'Daniel', 'Lai', '', 'eNHx4cwpJZ', False, False, False, True, ['Service']],
    # ['jtchan', 'Jennie', 'Chan', 'jtchan@vsb.bc.ca', 'PEd7Cbsp5e', True, True, True, False, []],
    # ['gjones', 'Gabriel', 'Jones', 'gjones@vsb.bc.ca', 'hg5MmWjhzL', True, True, True, False, []],
    # ['syip', 'Stacey', 'Yip', '', 'hg5MmWjhzL', False, False, False, True, ['Service']],
    # ['ccordoni', 'Chris', 'Cordoni', '', 'yUAp2WPMrJ', False, False, True, True, []],
    # ['jnbaker', 'Jean', 'Baker', '', 'AKsjFJ23ff', True, True, True, False, []],
]

PLIST = [
    [int(datetime.datetime.now().year) - 0, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999],
    [int(datetime.datetime.now().year) - 1, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999],
    [int(datetime.datetime.now().year) - 2, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999],
    [int(datetime.datetime.now().year) - 3, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999],
    [int(datetime.datetime.now().year) - 4, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999],
    [int(datetime.datetime.now().year) - 5, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999],
    [int(datetime.datetime.now().year) - 6, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999, 99.999],
]
GROUPS = ['Athletics', 'Service', 'Scholar', 'Fine Arts']
MODELS = ['Student', ]
PERMISSIONS = ['change', ]  # For now only view permission by default for all, others include add, delete, change

POINTTYPES = [
    ['SE', 0, 'See Student Comment Box'],
    ['SE', 1, 'Service Club'],
    ['SE', 2, 'Special Teacher Service'],
    ['SE', 3, 'Library Club'],
    ['SE', 4, 'Grad Service'],
    ['SE', 5, 'Scorer/Timer/Referee'],
    ['SE', 6, 'Team Manager'],
    ['SE', 7, 'Lost and Found'],
    ['SE', 8, 'Annual/Yearbook'],
    ['SE', 9, 'Service to Counselling Dep\'t'],
    ['SE', 11, 'Grad Committee'],
    ['SE', 12, 'Mini Student Council'],
    ['SE', 13, 'Student Council'],
    ['SE', 14, 'Awards Committee'],
    ['SE', 15, 'Canadian Cancer Club'],
    ['SE', 16, 'Environmental Club'],
    ['SE', 17, 'World Vision Club'],
    ['SE', 18, 'Sound and Stage'],
    ['SE', 19, 'Stage Crew Service'],
    ['SE', 21, 'RoadSense (ProjectZero)'],
    ['SE', 22, 'Service to Admin'],
    ['SE', 23, 'Fashion Show'],
    ['SE', 24, 'Poster Club'],
    ['SE', 25, 'Food Service Club'],
    ['SE', 26, 'Multicultural Club'],
    ['SE', 27, 'Model UN Club'],
    ['SE', 28, 'Marketing/Advertising Club'],
    ['SE', 29, 'Electronics Club'],
    ['SE', 31, 'Service to Drama Dep\'t'],
    ['SE', 32, 'Annual Advertising'],
    ['SE', 33, 'Service to Musical Prod'],
    ['SE', 34, 'Camp Leader'],
    ['SE', 35, 'Camp Assistant'],
    ['SE', 36, 'Gender Equality Committee'],
    ['SE', 37, 'Office/Secretarial Help'],
    ['SE', 38, 'First Nations Club'],
    ['SE', 39, 'Peer Tutoring (Non Cred)'],
    ['SE', 41, 'Music Student Executive'],
    ['SE', 42, 'Mini School Freeze Fest'],
    ['SE', 43, 'Service to Cafeteria'],
    ['SE', 44, 'Service to Athletics'],
    ['SE', 45, 'New or Static Club'],
    ['SE', 46, 'Global Issues Club'],
    ['SE', 47, 'Service to Art Dep\'t'],
    ['SE', 48, 'GSA Club'],
    ['SE', 49, 'Conference Committee'],
    ['SE', 51, 'Service to Special Ed'],
    ['SE', 52, 'Marking for teachers'],
    ['SE', 53, 'Westside Youth Advisory'],
    ['SE', 54, 'Computer or Webpage Service'],
    ['SE', 55, 'Service to Music Dep\'t'],
    ['SE', 56, 'Organising for Fundraising'],
    ['SE', 57, 'Service to Tech Studies'],
    ['SE', 58, 'Mini School Orientation'],
    ['SE', 59, 'Service to Mini School'],
    ['SE', 61, 'Service to Home Ec Dep\'t'],
    ['SE', 62, 'Service to First Nations'],
    ['SE', 63, 'School Newspaper'],
    ['SE', 64, 'Leadership Activity'],
    ['SE', 65, 'PAC related service'],
    ['SE', 66, 'Organisation of Event'],
    ['SE', 67, 'Service to Science Dep\'t'],
    ['SE', 68, 'Team Coach (for service)'],

    ['AT', 0, 'See Student Comment Box'],
    ['AT', 1, 'Bantam Fieldhockey'],
    ['AT', 2, 'Juvenile Fieldhockey'],
    ['AT', 3, 'Junior Fieldhockey'],
    ['AT', 4, 'Senior Fieldhockey'],
    ['AT', 5, 'Bantam Basketball'],
    ['AT', 6, 'Juvenile Basketball'],
    ['AT', 7, 'Junior Basketball'],
    ['AT', 8, 'Senior Basketball'],
    ['AT', 9, 'Bantam Volleyball'],
    ['AT', 11, 'Juvenile Volleyball'],
    ['AT', 12, 'Junior Volleyball'],
    ['AT', 13, 'Senior Volleyball'],
    ['AT', 14, 'Bantam Soccer'],
    ['AT', 15, 'Juvenile Soccer'],
    ['AT', 16, 'Junior Soccer'],
    ['AT', 17, 'Senior Soccer'],
    ['AT', 18, 'Bantam Badminton'],
    ['AT', 19, 'Juvenile Badminton'],
    ['AT', 21, 'Junior Badminton'],
    ['AT', 22, 'Senior Badminton'],
    ['AT', 23, 'Softball'],
    ['AT', 27, 'Rugby'],
    ['AT', 32, 'Gymnastics'],
    ['AT', 36, 'Track and Field'],
    ['AT', 41, 'Cross Country'],
    ['AT', 45, 'Golf'],
    ['AT', 49, 'Swimming'],
    ['AT', 54, 'Tennis'],
    ['AT', 58, 'Team Coach'],
    ['AT', 63, 'Outside Extramural Team'],
    ['AT', 64, 'Ice Hockey'],
    ['AT', 65, 'Water Polo'],
    ['AT', 66, 'Girl\'s Rugby (Spring+)'],
    ['AT', 67, 'Ultimate Frisbee'],
    ['AT', 68, 'Wrestling'],
    ['AT', 69, 'Mountain Biking'],
    ['AT', 71, 'Skiing / Snow Boarding'],
    ['AT', 72, 'Premier Soccer'],
    ['AT', 73, 'Cheerleading / Dance Team'],
    ['AT', 74, 'Team Manager (athletic points)'],

    ['FA', 0, 'See Student Comment Box'],
    ['FA', 1, 'Vocal Jazz'],
    ['FA', 2, 'Choir'],
    ['FA', 3, 'Stage Hand'],
    ['FA', 4, 'Musical Production'],
    ['FA', 5, 'Drama Club'],
    ['FA', 6, 'Beginner\'s Band'],
    ['FA', 7, 'Concert Band'],
    ['FA', 8, 'Intermediate Band'],
    ['FA', 9, 'Concert Choir'],
    ['FA', 11, 'Theatre Sports & Plays'],
    ['FA', 12, 'Jazz Combo'],
    ['FA', 13, 'Chamber Choir'],
    ['FA', 14, 'Vocal Jazz'],  # codes 1 and 14 are the same
    ['FA', 15, 'Pit Orchestra'],
    ['FA', 16, 'Acting Performance'],
    ['FA', 17, 'Improv Team/Games'],
    ['FA', 18, 'Directing Performances'],
    ['FA', 19, 'Theatre Sports'],
    ['FA', 21, 'One Act Plays'],
    ['FA', 22, 'Concert(s) / Performance(s)'],
    ['FA', 23, 'Vocal Ensemble'],
    ['FA', 24, 'Point Grey Dance Team'],
    ['FA', 25, 'Drama Department Activity'],
    ['FA', 26, 'Art Department Activity'],
    ['FA', 27, 'Music Department - Band'],
    ['FA', 27, 'Music Department - Choir'],
    ['FA', 27, 'Music Department - Concert'],
    ['FA', 27, 'Music Department Activity'],

]


class Command(BaseCommand):
    help = 'Creates 4 default groups for users and create pgadmin'

    def handle(self, *args, **options):
        for group in GROUPS:
            new_group, created = Group.objects.get_or_create(name=group)
            for model in MODELS:
                for permission in PERMISSIONS:
                    name = f'Can {permission} {model}'

                    try:
                        model_add_perm = Permission.objects.get(name=name)
                    except Permission.DoesNotExist:
                        logging.warning(f"Permission not found with name '{name}'.")
                        continue

                    new_group.permissions.add(model_add_perm)

        for u in USERS:
            username, first, last, email, pwd, is_super, is_staff, can_view, no_entry, groups = u
            try:
                user = User.objects.create_user(username=username, email=email, password=pwd)
            except Exception as e:
                print(e)
                logging.warning(f"Error creating user with name '{u[0]}'.")
                user = User.objects.get(username=u[0])
                user.email = email

            user.first_name = first
            user.last_name = last

            user.is_superuser = is_super
            user.is_staff = is_staff
            user.can_view = can_view
            user.no_entry = no_entry
            user.save()

            for group in groups:
                Group.objects.get(name=group).user_set.add(user)
            print(f"Updated '{username}' and with groups '{groups}'")

        for u in POINTTYPES:
            category, code, description = u
            if len(description) > 30:
                logging.warning(f'Error creating Code {code} due to description length')
            try:
                point = PointCodes.objects.get(catagory=category, code=code)
                point.description = description
                point.save()
                print(f'Updated Code {code} of type {category} with description: {description}')
            except PointCodes.DoesNotExist:
                point = PointCodes.objects.create(catagory=category, code=code, description=description)
                print(f'Created Code {code} of type {category} with description: {description}')

        for plist in PLIST:
            try:
                PlistCutoff.objects.create(year=plist[0],
                                           grade_8_T1=plist[1], grade_8_T2=plist[2],
                                           grade_9_T1=plist[3], grade_9_T2=plist[4],
                                           grade_10_T1=plist[5], grade_10_T2=plist[6],
                                           grade_11_T1=plist[7], grade_11_T2=plist[8],
                                           grade_12_T1=plist[9], grade_12_T2=plist[10])
            except Exception as e:
                print(e)
                logging.warning(f"Error creating Plist with year '{plist[0]}'.")

        try:
            Configuration.objects.get()
        except Configuration.DoesNotExist:
            Configuration.objects.create()
            print(f'Created default configurations')

        print("Created default definitions, user and groups.")
