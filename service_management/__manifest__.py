{
    "name": "Service Management (Helpdesk + Field Service)",
    "summary": "Serial-number driven tickets, warranty, SLA reminders, GPS check-in, video call",
    "version": "18.0.1.0",
    "category": "Services/Helpdesk",
    "author": "ManojThombare",
    "license": "LGPL-3",
    "depends": [
        "base",
        "helpdesk",
        "stock",             
        "mail", 
        "project",
        "contacts",
    ],
    "data": [
        
        "data/mail_template.xml",
        "data/automated_actions.xml",
        "views/menus.xml",
        "views/stock_production_lot_view.xml",
        "views/product_template_view.xml",
        "views/helpdesk_team_views.xml",
        "views/helpdesk_ticket_views.xml",
        "views/fsm_order_views.xml",
    ],
    "application": True,
    "installable": True,
}
