# AstroBase Server

* http://uilennest.net:81/astrobase

A lightweight Astrophotography pipeline.
Raw images are submitted to astrometry.net for positioning in the sky and meta data extraction.
The metadata and images are stored in a database and on a backend filesystem and can be accessed by a REST API.

The backend has a basic GUI, and can use the Django Admin application.

<p align="center">
  <img src="https://github.com/nvermaas/MyAstroBase/blob/master/docs/AstroBase.png"/>
</p>

Changelog
-
1.1.0 (26 oct 2019)
* Adding 'upload file' functionality to the backend

1.0.0 (24 oct 2019)
* First release