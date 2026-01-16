/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SaaSUsageBanner extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            currentUsers: 0,
            userLimit: 0,
            percentage: 0,
            showWarning: false,
            warningLevel: 'success',
        });

        onWillStart(async () => {
            await this.loadUsageData();
        });
    }

    async loadUsageData() {
        const data = await this.rpc("/web/dataset/call_kw/res.users/get_saas_usage_info", {
            model: "res.users",
            method: "get_saas_usage_info",
            args: [],
            kwargs: {},
        });
        
        Object.assign(this.state, data);
    }

    get alertClass() {
        if (this.state.percentage >= 95) return 'alert-danger';
        if (this.state.percentage >= 80) return 'alert-warning';
        return 'alert-info';
    }

    get progressBarClass() {
        if (this.state.percentage >= 95) return 'bg-danger';
        if (this.state.percentage >= 80) return 'bg-warning';
        return 'bg-success';
    }
}

SaaSUsageBanner.template = "saas_client_agent.UsageBanner";

registry.category("main_components").add("SaaSUsageBanner", {
    Component: SaaSUsageBanner,
});
