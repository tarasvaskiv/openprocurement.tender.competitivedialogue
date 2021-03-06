# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from openprocurement.tender.openeu.tests.base import test_lots
from openprocurement.api.tests.base import snitch
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_features_tender_eu_data,
    test_bids,
    test_shortlistedFirms,
    test_tender_stage2_data_eu,
    test_tender_stage2_data_ua
)
from openprocurement.tender.belowthreshold.tests.auction import (
    TenderAuctionResourceTestMixin,
    TenderLotAuctionResourceTestMixin,
    TenderMultipleLotAuctionResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.auction_blanks import (
    # TenderStage2EU(UA)SameValueAuctionResourceTest
    post_tender_auction_not_changed,
    post_tender_auction_reversed,
    # TenderStage2EU(UA)FeaturesAuctionResourceTest
    get_tender_auction_feature,
)
from openprocurement.tender.competitivedialogue.tests.stage2.auction_blanks import (
    # # TenderStage2EU(UA)MultipleLotAuctionResourceTest
    patch_tender_with_lots_auction,
)

author = deepcopy(test_bids[0]["tenderers"][0])
author['identifier']['id'] = test_shortlistedFirms[0]['identifier']['id']
author['identifier']['scheme'] = test_shortlistedFirms[0]['identifier']['scheme']

test_tender_bids = deepcopy(test_bids[:2])
for test_bid in test_tender_bids:
    test_bid['tenderers'] = [author]


class TenderStage2EUAuctionResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderAuctionResourceTestMixin):
    initial_auth = ('Basic', ('broker', ''))
    initial_bids = deepcopy(test_tender_bids)

    def setUp(self):
        super(TenderStage2EUAuctionResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification")

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], self.tender_token),
                {'data': {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.status, "200 OK")


class TenderStage2EUSameValueAuctionResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    # initial_status = 'active.auction'
    tenderer_info = deepcopy(author)
    initial_bids = [
        {
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfQualified': True,
            'selfEligible': True
        }
        for i in range(3)
    ]

    def setUp(self):
        """ Init tender and set status to active.auction """
        super(TenderStage2EUSameValueAuctionResourceTest, self).setUp()
        auth = self.app.authorization
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], "active.pre-qualification")

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               self.tender_token),
                                           {'data': {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status('active.auction', {'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.auction")
        self.app.authorization = auth

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderStage2EULotAuctionResourceTest(TenderLotAuctionResourceTestMixin, TenderStage2EUAuctionResourceTest):
    initial_lots = deepcopy(test_lots)


class TenderStage2EUMultipleLotAuctionResourceTest(TenderMultipleLotAuctionResourceTestMixin, TenderStage2EUAuctionResourceTest):
    initial_lots = deepcopy(2 * test_lots)

    test_patch_tender_auction = snitch(patch_tender_with_lots_auction)


class TenderStage2EUFeaturesAuctionResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_data = test_features_tender_eu_data
    features = [
            {
                "code": "OCDS-123454-AIR-INTAKE",
                "featureOf": "item",
                "relatedItem": "1",
                "title": u"Потужність всмоктування",
                "title_en": u"Air Intake",
                "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
                "enum": [
                    {
                        "value": 0.05,
                        "title": u"До 1000 Вт"
                    },
                    {
                        "value": 0.1,
                        "title": u"Більше 1000 Вт"
                    }
                ]
            },
            {
                "code": "OCDS-123454-POSTPONEMENT",
                "featureOf": "tenderer",
                "title": u"Відстрочка платежу",
                "title_en": u"Postponement of payment",
                "description": u"Термін відстрочки платежу",
                "enum": [
                    {
                        "value": 0.05,
                        "title": u"До 90 днів"
                    },
                    {
                        "value": 0.1,
                        "title": u"Більше 90 днів"
                    }
                ]
            }
        ]
    tenderer_info = deepcopy(author)
    initial_bids = [
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.05,
                }
                for i in features
            ],
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfQualified': True,
            'selfEligible': True
        },
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.1,
                }
                for i in features
            ],
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 479,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfQualified': True,
            'selfEligible': True
        }
    ]
    initial_status = 'active.auction'

    def setUp(self):
        self.app.authorization = ('Basic', ('broker', ''))
        data = test_tender_stage2_data_eu.copy()
        item = data['items'][0].copy()
        item['id'] = "1"
        data['items'] = [item]
        data['features'] = [
            {
                "code": "OCDS-123454-AIR-INTAKE",
                "featureOf": "item",
                "relatedItem": "1",
                "title": u"Потужність всмоктування",
                "title_en": u"Air Intake",
                "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
                "enum": [
                    {
                        "value": 0.05,
                        "title": u"До 1000 Вт"
                    },
                    {
                        "value": 0.1,
                        "title": u"Більше 1000 Вт"
                    }
                ]
            },
            {
                "code": "OCDS-123454-POSTPONEMENT",
                "featureOf": "tenderer",
                "title": u"Відстрочка платежу",
                "title_en": u"Postponement of payment",
                "description": u"Термін відстрочки платежу",
                "enum": [
                    {
                        "value": 0.05,
                        "title": u"До 90 днів"
                    },
                    {
                        "value": 0.1,
                        "title": u"Більше 90 днів"
                    }
                ]
            }
        ]
        self.create_tender(initial_data=data, initial_bids=self.initial_bids)

    test_get_tender_auction = snitch(get_tender_auction_feature)


class TenderStage2UAAuctionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderAuctionResourceTestMixin):
    initial_status = 'active.tendering'
    initial_bids = deepcopy(test_tender_bids)


class TenderStage2UASameValueAuctionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.auction'
    initial_bids = [
        {
            "tenderers": [
                author
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfEligible': True, 'selfQualified': True,
        }
        for i in range(3)
    ]

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderStage2UALotAuctionResourceTest(TenderLotAuctionResourceTestMixin, TenderStage2UAAuctionResourceTest):
    initial_lots = test_lots
    initial_data = test_tender_stage2_data_ua


class TenderStage2UAMultipleLotAuctionResourceTest(TenderMultipleLotAuctionResourceTestMixin, TenderStage2UAAuctionResourceTest):
    initial_lots = deepcopy(2 * test_lots)

    test_patch_tender_auction = snitch(patch_tender_with_lots_auction)


class TenderStage2UAFeaturesAuctionResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    features = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "item",
            "relatedItem": "1",
            "title": u"Потужність всмоктування",
            "title_en": u"Air Intake",
            "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [
                {
                    "value": 0.05,
                    "title": u"До 1000 Вт"
                },
                {
                    "value": 0.1,
                    "title": u"Більше 1000 Вт"
                }
            ]
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": u"Відстрочка платежу",
            "title_en": u"Postponement of payment",
            "description": u"Термін відстрочки платежу",
            "enum": [
                {
                    "value": 0.05,
                    "title": u"До 90 днів"
                },
                {
                    "value": 0.1,
                    "title": u"Більше 90 днів"
                }
            ]
        }
    ]
    tenderer_info = deepcopy(author)
    initial_bids = [
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.05,
                }
                for i in features
                ],
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfQualified': True,
            'selfEligible': True
        },
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.1,
                }
                for i in features
                ],
            "tenderers": [
                tenderer_info
            ],
            "value": {
                "amount": 479,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfQualified': True,
            'selfEligible': True
        }
    ]
    initial_status = 'active.auction'

    def setUp(self):
        self.app.authorization = ('Basic', ('broker', ''))
        data = test_tender_stage2_data_ua.copy()
        item = data['items'][0].copy()
        item['id'] = "1"
        data['items'] = [item]
        data['features'] = [
            {
                "code": "OCDS-123454-AIR-INTAKE",
                "featureOf": "item",
                "relatedItem": "1",
                "title": u"Потужність всмоктування",
                "title_en": u"Air Intake",
                "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
                "enum": [
                    {
                        "value": 0.05,
                        "title": u"До 1000 Вт"
                    },
                    {
                        "value": 0.1,
                        "title": u"Більше 1000 Вт"
                    }
                ]
            },
            {
                "code": "OCDS-123454-POSTPONEMENT",
                "featureOf": "tenderer",
                "title": u"Відстрочка платежу",
                "title_en": u"Postponement of payment",
                "description": u"Термін відстрочки платежу",
                "enum": [
                    {
                        "value": 0.05,
                        "title": u"До 90 днів"
                    },
                    {
                        "value": 0.1,
                        "title": u"Більше 90 днів"
                    }
                ]
            }
        ]
        self.create_tender(initial_data=data, initial_bids=self.initial_bids)

    test_get_tender_auction = snitch(get_tender_auction_feature)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUSameValueAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUFeaturesAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UASameValueAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAFeaturesAuctionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
