/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

patch(Dialog.prototype,{
    setup() {
        super.setup();
        const companyTitle = session.odoo_tittle_name || "ITeSolution Software Services";
        if (this.title && typeof this.title === 'string') {
            this.title = this.title.replace(/Odoo/g, companyTitle);
        }
    },
});
