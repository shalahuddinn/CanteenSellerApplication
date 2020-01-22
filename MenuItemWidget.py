from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout)

from HelperMethod import formatRupiah


class MenuItemWidget(QWidget):
    def __init__(self, id, image, name, price, category, availability, qtyAvailable, qtyOnBooked):
        super().__init__()

        self.id = id
        self.image = image
        self.name = name
        self.price = price
        self.category = category
        self.availability = availability
        self.qtyAvailable = qtyAvailable
        self.qtyOnBooked = qtyOnBooked

        self.imageLabel = QLabel()
        self.imageLabel.setPixmap(self.image)

        self.nameLabel = QLabel()
        self.nameLabel.setText(self.name)

        self.priceLabel = QLabel()
        self.priceLabel.setText(formatRupiah(price))

        self.availabilityLabel = QLabel()

        self.qtyAvailableLabel = QLabel()
        self.qtyAvailableLabel.setText("Qty Available: {}".format(self.qtyAvailable))

        self.qtyOnBookedLabel = QLabel()
        self.qtyOnBookedLabel.setText("Qty On Booked: {}".format(self.qtyOnBooked))

        self.editButton = QPushButton("Edit")

        if self.availability:
            self.availabilityLabel.setText("Ready")
        else:
            self.availabilityLabel.setText("Not Available")

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.nameLabel)
        self.vbox.addWidget(self.availabilityLabel)
        self.vbox.addWidget(self.priceLabel)

        self.vbox2 = QVBoxLayout()
        self.vbox2.addWidget(self.qtyAvailableLabel)
        self.vbox2.addWidget(self.qtyOnBookedLabel)

        self.hbox = QHBoxLayout()

        self.hbox.addWidget(self.imageLabel)
        self.hbox.addLayout(self.vbox)
        self.hbox.addLayout(self.vbox2)
        self.hbox.addWidget(self.editButton)

        self.setLayout(self.hbox)
