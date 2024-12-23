from odoo.http import request, route

from odoo.addons.website.controllers.main import Website


class Website(Website):
    # @route()
    # def autocomplete(self, search_type=None, term=None, order=None, limit=5, max_nb_chars=999, options=None):
    #     request.update_context(whole_pack_price=True)
    #     return super().autocomplete(
    #         search_type=search_type,
    #         term=term,
    #         order=order,
    #         limit=limit,
    #         max_nb_chars=max_nb_chars,
    #         options=options
    #     )



    # def shop(
    #     self,
    #     page=0,
    #     category=None,
    #     search="",
    #     min_price=0.0,
    #     max_price=0.0,
    #     ppg=False,
    #     **post,
    # ):
    #     request.update_context(whole_pack_price=True)
    #     return super().shop(
    #         page=page,
    #         category=category,
    #         search=search,
    #         min_price=min_price,
    #         max_price=max_price,
    #         ppg=ppg,
    #         **post,
    #     )
