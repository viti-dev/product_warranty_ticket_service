/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

patch(WebClient.prototype, {
    setup() {
        super.setup(); 

        const companyTitle = session.odoo_tittle_name || "ITeSolution Software Services";
        const titleService = useService("title");


        titleService.setParts({
            zopenerp: "ITeSolution Software Services",
//            zopenerp: companyTitle,
        });
    },
});
