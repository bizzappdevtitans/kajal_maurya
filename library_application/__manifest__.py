{
    "name": "Library Application",
    "summary": "Used for library management",
    "website": "https://bizzappdev.com",
    "author": "bizzappdev",
    "version": "15.0.1.0.0",
    "category": "uncategorized",
    "depends": ["base",'mail'],
    "data": [
        "security/ir.model.access.csv",
        "views/book_details_views.xml",
        "views/book_menu_views.xml",

    ],
    "application": True,
    "license": "LGPL-3",
    "sequence": -100,
}
