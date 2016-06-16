
import lxml.etree as ET
from PIL import Image
import os
from os import listdir
import sys
import settings


class ContentPreprocessor:

    def __init__(self, xsl_file, course):
        self.xsl_file = xsl_file
        self.course = course

    def preprocess_course(self):
        """ Perform the course pre-processing. This include converting the course contents to HTML and optimize the
            course images"""
        self.course_to_html()
        self.optimize_images()

    def course_to_html(self):

        i = 1
        for section in self.course.sections:
            section.title = self.content_to_html(section.title)
            progress = str(i * 100 / len(self.course.sections)) + '%'
            print '\r> Applying XSLT to the course (' + progress + ')',
            sys.stdout.flush()

            for session in section.sessions:
                session.title = self.content_to_html(session.title)
                session.content = self.content_to_html(session.content)

            i += 1
        print '\r> Applying XSLT to the course (100%). Done.'

    def content_to_html(self, content):
        """Apply XSLT to the content of the course and returns the converted HTML text"""
        print content
        dom = ET.XML(content, ET.XMLParser(target=ET.TreeBuilder()))
        xslt = ET.parse(self.xsl_file)
        transform = ET.XSLT(xslt)
        newdom = transform(dom)
        return ET.tostring(newdom, pretty_print=True)

    def optimize_images(self):
        print '\nBegining image optimization'
        images_dir = os.path.join(settings.OUTPUT_PATH, 'temp', 'images')
        size_saved = 0
        i = 1
        for image_file in listdir(images_dir):
            image_path = os.path.join(images_dir, image_file)
            initial_size = os.stat(image_path).st_size
            progress = str(i * 100 / len(listdir(images_dir))) + '%'
            print '\r  > Optimizing images (' + progress + ')',
            sys.stdout.flush()
            image = Image.open(image_path)
            new_width = 300
            width_percent = (new_width / float(image.size[0]))
            new_height = int((float(image.size[1]) * float(width_percent)))
            image.thumbnail((new_width, new_height), Image.ANTIALIAS)
            extension = image_file.split(".")[-1]
            if extension == 'jpg':
                image.save(image_path, optimize=True, quality=90)
            else:
                image.save(image_path)
            final_size = os.stat(image_path).st_size
            size_saved += initial_size - final_size
            i += 1
        print '\r  > Optimizing images (100%). Done. ' + str(size_saved/1024) + 'KB saved.'
