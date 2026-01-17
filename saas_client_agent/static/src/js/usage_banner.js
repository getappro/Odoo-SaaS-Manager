/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class SaaSUsageBanner extends Component {
    static template = "saas_client_agent.UsageBanner";

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
        try {
            const data = await this.rpc("/web/dataset/call_kw", {
                model: "res. users",
                method: "get_saas_usage_info",
                args: [],
                kwargs: {},
            });

            if (data) {
                Object.assign(this.state, data);
            }
        } catch (error) {
            console. error("Failed to load SaaS usage data:", error);
        }
    }

    get alertClass() {
        if (this. state.percentage >= 95) return 'alert-danger';
        if (this.state.percentage >= 80) return 'alert-warning';
        return 'alert-info';
    }

    get progressBarClass() {
        if (this.state.percentage >= 95) return 'bg-danger';
        if (this.state.percentage >= 80) return 'bg-warning';
        return 'bg-success';
    }
}

// Register as system bar component (appears at top of interface)
registry.category("systray").add("SaaSUsageBanner", {
    Component:  SaaSUsageBanner,
}, { sequence: 100 });