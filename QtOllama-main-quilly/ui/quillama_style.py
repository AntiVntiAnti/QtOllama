stylesheet = """

QWidget {
font: 13pt "Helvetica";
background:#151515;
color:rgb(255,255,255);
}
/* /////////////////////////////////////////////////////////////////////////////
QTimeEdit, QDoubleSpinBox, QSpinBox
///////////////////////////////////////////////////////////////////////////// */
QDoubleSpinBox,
QSpinBox {
border:none;
}
QTextEdit {border:none; }
/* /////////////////////////////////////////////////////////////////////////////
QLabel
///////////////////////////////////////////////////////////////////////////// */
QLabel {
background:transparent;
}

/* /////////////////////////////////////////////////////////////////////////////
QComboBox
///////////////////////////////////////////////////////////////////////////// */
QComboBox {
background-color: transparent;
border:1px inset rgb(28,32,23);
border-radius:2px;
padding: 3px;
}

/* /////////////////////////////////////////////////////////////////////////////
QLineEdit
/////////////////////////////////////////////////////////////////////////////*/
QLineEdit {
border: none;
background: transparent;
}
QLineEdit:hover {
border-bottom:1px solid rgba(123, 123, 123, 150);
}
QLineEdit:focus {
border-bottom:1px solid rgba(123, 123, 123, 200);
}

/* /////////////////////////////////////////////////////////////////////////////
QCheckBox
///////////////////////////////////////////////////////////////////////////// */
QCheckBox::indicator {
font-weight:bold;
background-color: transparent;
border: 2px solid rgb(33,143,109);
border-radius: 6px;
width: 8px;
height: 8px;
margin-left:8px;
margin-right:8px;
}
QCheckBox::indicator:hover {
border: 2px solid white;
}
QCheckBox::indicator:checked {
background: rgb(33,143,109);
border: 2px solid rgb(33,143,109);
}

/* //////////////////////////////////////////////////////////////
QSlider HORIZONTALALALALALAL
////////////////////////////////////////////////////////////// */
QSlider:horizontal {
background:transparent;
border:none;
min-height:18px;
}
QSlider::groove:horizontal {
border-radius: 8px;
height: 16px;
margin: 0px;
background:rgb(22, 22, 22);
}

QSlider::groove:horizontal:hover {
background: rgb(38, 38, 38);
}
QSlider::handle:horizontal {
background: rgb(255, 255, 255);
height: 16px;
width: 16px;
margin: 0px;
border-radius:8px;
}
QSlider::sub-page:horizontal {
background:transparent;
}
QSlider::handle:horizontal:hover {
background-color: white;
}
QSlider::handle:horizontal:pressed {
background-color:white;
}
/* ///////////////////////////////////////////////////////////
QSlider VERTICAL
////////////////////////////////////////////////////////////// */
QSlider::groove:vertical {
border-radius: 11px;
width: 22px;
margin: 0px;
background-color: rgba(33,33,33,100);
}

QSlider::groove:vertical:hover {
background-color: rgba(44,44,44,100);
}
QSlider::handle:vertical {
background-color: rgb(255, 88, 71);
border: none;
height: 22px;
width: 22px;
margin: 0px;
border-radius: 11px;
}
QSlider::handle:vertical:hover {
background-color: rgb(195, 155, 255);
}
QSlider::handle:vertical:pressed {
background-color: rgb(255, 121, 198);
}

/* /////////////////////////////////////////////////////////////////////////////
Time/DateEdit
///////////////////////////////////////////////////////////////////////////// */
QTimeEdit,
QDateEdit {
background-color: transparent;
border:None;
}

/* //////////////////////////////////////////////////////////////////////////////
AGENDA SIDEBAR BTN primer
////////////////////////////////////////////////////////////////////////////// */

#sender {
padding:4px;
color:rgb(210, 191, 234);
border:2px solid rgb(210, 191, 234);
border-radius:21px;
background:transparent;
min-width:30px;
max-width:30px;
min-height:30px;
max-height:30px;

}
#sender:hover {
border-radius:20px;
border:2px solid rgb(210, 191, 234);
background:rgb(210, 191, 234);
color:rgb(110, 91, 134);
}

#sender:pressed {
margin-top:0px;
margin-left:0px;border:2px solid rgb(210, 191, 234);
}
QPushButton {
color:#fff;
text-align:left;
border-radius:6px;
font-weight:100;
padding:6px;
min-width:55px;
max-height:55px;
text-align:center;
}
QPushButton:hover {
color:#fff;
padding: 2px;
font-size:9pt;
margin:2px 2px 0px 0px;
padding-top:4px;
}

QPushButton:pressed {
font-weight:bold;
font-size:9pt;
margin:0px;
color:#fff;
}


/* //////////////////////////////////////////////////////////////
QDateEdit
////////////////////////////////////////////////////////////// */

QDateEdit {
font-size:10pt;
}

QComboBox {border:none;}
"""
