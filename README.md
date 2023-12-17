
## Smart Image Merge

A smart and simple application to merge (stitch) images automatically.  

<br/><br/>
<img src='https://github.com/ivangermes/SmartImageMerge/assets/645880/cf6a57ae-334e-4029-adea-56d303db98f0' width='800'>
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
Just download and run.


### Dev notes
#### ft.Container behavior.

Some kind of magic with ft.Container.
It fills the whole area or not, whether padding, aligment and content properties are set or not.
This is the case, at least for flet==0.14

I haven't found a way to color the area in any other way than using ft.Container.
To avoid confusing behavior, I use ft.Stack with two ft.Container. One for the background, the other to indent the picture.

#### Build executable files
`flet pack src/stitcher.py --name stitcher --icon icon.png --product-name SmartImageMerge --file-description SmartImageMerge --product-version XXX`


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
- [ ] building for linux and windows
- [ ] add video tutorial
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
- [ ] update flet to latest version
- [ ] add translations
- [ ] make async (?)
- [ ] sign windows version
