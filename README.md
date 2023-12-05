
## TODO:

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
- [ ] exception and error handling
- [ ] tune stitching
- [ ] check that windows clear TMP files
- [x] store and restore last file picker path
- [ ] add icon
- [ ] building for linux and windows
- [ ] add translations
- [ ] make async (?)
- [ ] update flet to new version


## ft.Container behavior.

Some kind of magic with ft.Container.
It fills the whole area or not, whether padding, aligment and content properties are set or not.
This is the case, at least for flet==0.14

I haven't found a way to color the area in any other way than using ft.Container.
To avoid confusing behavior, I use ft.Stack with two ft.Container. One for the background, the other to indent the picture.