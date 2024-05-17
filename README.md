# SATT
Semi-Automatic Thresholding Tool (SATT) for species identification and location mapping using an object detection pipeline and trigonometry

The Tool utilises the NumPy, Pandas, GeoPandas, Shapely, and OpenCV Python libraries (Bradski, 2000; Gillies et al., 2007; McKinney, 2010; Jordahl, 2014; Harris et al., 2020). The ExifTool open-source software is used to read the embedded metadata of images, also known as the Exchangeable Image File Format (EXIF) (Harvey, 2016). 

The tool utilises Hue, Saturation, and Value (HSV) colour space parameters as well as a kernel search. The tool has been packaged into a single executable file using the Python PyQt5 library to develop the Graphical User Interface (GUI) and the python library PyInstaller to compile the software into a single executable file. This enables non-expert users to utilise the software without needing to install other programmes. An Advanced popout window was built so that users could adjust the thresholding parameters, kernel shape, and minimum object size easily and apply this to a subsample of images for initial fine-tuning of the semi-automatic workflow. 

Once flowers are detected, a bounding box labels the object and determines the object height and width. Within the software a minimum pixel search size is used to remove excess noise (e.g. commission errors) that are occasionally included within the HSV thresholding step of the workflow. 


REFERENCES
Bradski, G. (2000). "The opencv library." Dr. Dobb's Journal: Software Tools for the Professional Programmer 25(11): 120-123.
Gillies, S., A. Bierbaum, K. Lautaportti and O. Tonnhofer (2007). "Shapely: manipulation and analysis of geometric objects." Available At: "https://github.com/Toblerity/Shapely".
Harris, C. R., K. J. Millman, S. J. Van Der Walt, R. Gommers, P. Virtanen, D. Cournapeau, E. Wieser, J. Taylor, S. Berg and N. J. Smith (2020). "Array programming with NumPy." Nature 585(7825): 357-362.
Harvey, P. (2016). ExifTool. Available at: https://exiftool.org/.
Jordahl, K. (2014). "GeoPandas: Python tools for geographic data." URL: https://github. com/geopandas/geopandas 3.
McKinney, W. (2010). Data structures for statistical computing in Python. SciPy.
