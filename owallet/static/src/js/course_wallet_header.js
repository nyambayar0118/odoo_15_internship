odoo.define('owallet.CourseWalletHeader', function (require) {
    "use strict";

    var KanbanController = require('web.KanbanController');
    var rpc = require('web.rpc');

    KanbanController.include({

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if (self.modelName === 'olearn2.course') {
                    self._addWalletHeader();
                }
            });
        },

        _addWalletHeader: function () {
            var self = this;

            // Check if user is a student
            rpc.query({
                model: 'res.users',
                method: 'has_group',
                args: ['olearn2.group_student'],
            }).then(function (isStudent) {
                if (!isStudent) return;

                // Check user is not a teacher
                return rpc.query({
                    model: 'res.users',
                    method: 'has_group',
                    args: ['olearn2.group_teacher'],
                }).then(function (isTeacher) {
                    if (isTeacher) return;

                    // Get balance
                    return rpc.query({
                        model: 'olearn2.course',
                        method: 'get_current_user_balance',
                        args: [],
                    }).then(function (data) {
                        self._renderWalletHeader(data);
                    });
                });
            });
        },

        _renderWalletHeader: function (data) {
            var self = this;
            var formattedAmount = data.amount.toLocaleString();
            var balanceText = data.currency_position === 'before'
                ? data.currency_symbol + formattedAmount
                : formattedAmount + data.currency_symbol;

            var $header = $(`
                <div class="o_wallet_header" style="
                    background: linear-gradient(135deg, #1E90FF 0%, #0066CC 100%);
                    border-radius: 8px;
                    padding: 20px 24px;
                    margin-bottom: 16px;
                    box-shadow: 0 2px 8px rgba(30, 144, 255, 0.3);
                ">
                    <div style="display: flex; align-items: center; color: white; margin-bottom: 12px;">
                        <div>
                            <div style="font-size: 12px; opacity: 0.85; margin-bottom: 2px;">Миний дансны үлдэгдэл</div>
                            <div style="font-size: 24px; font-weight: 600;">${balanceText}</div>
                        </div>
                    </div>
                    <button class="btn btn-deposit" style="
                        background: white;
                        color: #1E90FF;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 6px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.2s ease;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    " onmouseover="this.style.background='#f0f8ff'; this.style.transform='translateY(-1px)';"
                       onmouseout="this.style.background='white'; this.style.transform='translateY(0)';">
                        <i class="fa fa-plus-circle" style="margin-right: 6px;"></i> Данс цэнэглэх заавар
                    </button>
                </div>
            `);

            $header.find('.btn-deposit').on('click', function () {
                self.do_action({
                    type: 'ir.actions.act_window',
                    name: 'Данс цэнэглэх заавар',
                    res_model: 'owallet.deposit.wizard.guide',
                    view_mode: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                });
            });

            this.$el.find('.o_kanban_view').prepend($header);
        },
    });
});