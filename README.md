
## Smart Image Merger

A smart and simple application to merge (stitch) images automatically.  

<br/>
<img src='https://github.com/ivangermes/SmartImageMerge/assets/645880/6be3f54d-aeed-426b-98ef-2d1588f51de4' width='800'>
<br/><br/>

If you have some oversized images that don't fit your flatbed scanner, the app lets you merge their scanned fragments.  
Merging the parts manually is difficult, since it's hard to arrange them perfectly even.   
This app joins such images automatically.  
Suitable for all things scanned: photos, drawings, maps, posters, etc.   


## About
Cross-platform ( Windows, Linux, Android, Web ).

Tech stack:
- OpenCV
- Flutter
- Python

## Install

Latest Linux and Windows versions here: https://github.com/ivangermes/SmartImageMerge/releases  
Just download, unzip and run.


### Dev notes
#### ft.Container behavior.

Some kind of magic with ft.Container.
It fills the whole area or not, whether padding, aligment and content properties are set or not.
This is the case, at least for flet==0.14

I haven't found a way to color the area in any other way than using ft.Container.
To avoid confusing behavior, I use ft.Stack with two ft.Container. One for the background, the other to indent the picture.

#### Build executable files

For Linux:  
`flet build --project stitcher --product "Smart Image Merger" --build-version xxx --module-name stitcher.py linux`

For Windows:
`flet build --project stitcher --product "Smart Image Merger" --build-version xxx --module-name stitcher.py windows`

Read https://flet.dev/docs/guides/python/packaging-app-for-distribution


### TODO:

- [x] add disable button on process
- [x] add preloader
- [x] add input images preview
- [x] add output images preview
- [x] delete in files
- [x] make states
- [x] styling
- [x] refactoring
- [x] type cheickng
- [x] add comments
- [x] basic exception and error handling
- [x] tune stitching
- [x] building for linux and windows
- [x] move to new build system
- [ ] check that windows clear TMP files
- [x] store and restore last file picker path
- [x] add icon
- [x] add screenshot or video
- [ ] improve rotated images stitchig
- [ ] add warining handling
- [ ] improve exception and error handling
- [ ] add tests
- [ ] add CI
- [ ] add CD
- [ ] add crop option
- [ ] memory usage improvment
- [ ] add translations
- [ ] make async (?)
