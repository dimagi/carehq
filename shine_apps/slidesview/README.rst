Slidesview app for SHINE
=========================

This app is the main viewer/dispatcher of casexml for image slides.

Getting Started
===============

Make sure the requirements are installed from the root carehq settings.  New apps unique for this app are sorl-thumbnails and PIL.

Windows, you may need to install a PIL binary for it to work, it doesn't pip well.

In order for the couch images to work with sorl-thumbnail, you need to premake the images into the filesystem.

To do this, you will need to run the simple script associated with this, the management command collect_images.


