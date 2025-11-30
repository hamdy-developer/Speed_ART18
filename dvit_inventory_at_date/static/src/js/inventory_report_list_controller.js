/** @odoo-module **/
import { registry } from "@web/core/registry";
import { InventoryReportListController } from "@stock/views/list/inventory_report_list_controller";
import { formView } from "@web/views/form/form_view";
import { InventoryReportListModel } from "@stock/views/list/inventory_report_list_model";
import { listView } from "@web/views/list/list_view";

export class CustomInventoryReportListController extends InventoryReportListController {
    async onClickInventoryAtDate() {
//            const options = await super.onClickInventoryAtDate();

        // Your custom implementation here
        // You can call super.onClickInventoryAtDate() if you want to include the original functionality

        // For example, let's log a message before calling the original method

        console.log("Custom onClickInventoryAtDate() is called");
        console.log(this.actionService)
//        console.log(this.props.context.params.action)
        console.log(this.props)
//        this.props.context.append("active_id", this.props.context.params.action);
        const context = {
            active_model: this.props.resModel,
        };
        if (this.props.context.default_product_id) {
            context.product_id = this.props.context.default_product_id;
        } else if (this.props.context.product_tmpl_id) {
            context.product_tmpl_id = this.props.context.product_tmpl_id;
        }
        if (this.props.context.inventory_at_date) {
            context.inventory_at_date = this.props.context.inventory_at_date;
        }
        this.actionService.doAction({
            res_model: "stock.quantity.history",
            views: [[false, "form"]],
            target: "new",
            type: "ir.actions.act_window",
            context,
        });

        // Call the original method
//        await super.onClickInventoryAtDate();

        // Additional custom logic after the original method is executed
    }
}
// Use the original controller from the original module
export const InventoryReportListView = {
    ...listView,
    Model: InventoryReportListModel,
    Controller: CustomInventoryReportListController, // Use your custom controller here
    buttonTemplate: 'InventoryReport.Buttons',
};

registry.category("views").add('inventory_report_list', InventoryReportListView, { force: true });
