# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestProjectTaskGeneratedWithProductPerformance(common.TransactionCase):

    def setUp(self):
        super(TestProjectTaskGeneratedWithProductPerformance, self).setUp()
        self.sale_model = self.env['sale.order']
        self.procurement_model = self.env['procurement.order']
        account_vals = {'name': 'account procurement service project',
                        'date_start': '2016-01-15',
                        'date': '2016-02-20'}
        self.account = self.env['account.analytic.account'].create(
            account_vals)
        project_vals = {'name': 'project procurement service project',
                        'analytic_account_id': self.account.id}
        self.project = self.env['project.project'].create(project_vals)
        service_product = self.env.ref('product.product_product_consultant')
        service_product.performance = 5.0
        service_product.route_ids = [
            (6, 0,
             [self.ref('procurement_service_project.route_serv_project')])]
        sale_vals = {
            'partner_id': self.ref('base.res_partner_1'),
            'partner_shipping_id': self.ref('base.res_partner_1'),
            'partner_invoice_id': self.ref('base.res_partner_1'),
            'pricelist_id': self.env.ref('product.list0').id,
            'project_id': self.account.id}
        sale_line_vals = {
            'product_id': service_product.id,
            'name': service_product.name,
            'product_uom_qty': 7,
            'product_uos_qty': 7,
            'product_uom': service_product.uom_id.id,
            'price_unit': service_product.list_price,
            'performance': 5.0}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order = self.sale_model.create(sale_vals)

    def test_project_task_generated_with_product_performance(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_line_id', '=', self.sale_order.order_line[0].id)]
        procurement = self.procurement_model.search(cond)
        self.assertEqual(
            len(procurement), 1,
            'Procurement not generated for product service')
        procurement.run()
        self.assertEqual(
            len(self.project.tasks), 1,
            'Task not generated from procurement')
        self.assertEqual(
            self.project.tasks[0].planned_hours, 35,
            'Error in calculated planned_hours')