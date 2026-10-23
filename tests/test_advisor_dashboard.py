"""Behavior checks for the shared advisor layout in the real Streamlit app."""
import unittest
import tempfile
from unittest.mock import patch
from uuid import uuid4

from advisor_layout import load_metric_order, save_metric_order
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / 'streamlit_app.py'
DEFAULTS = ['Satisfaction Score', 'Fixed right first time',
            'Spoke to advisor immediately', 'Kept informed']
EXTRA = 'Advisor provided video'


def advisor_doc():
    columns = ['Employee', 'Rank', *DEFAULTS, EXTRA, 'Completes']
    return {
        'dataset': {'title': 'Service Employee Rank', 'columns': columns, 'rows': [
            dict(zip(columns, ['Alex Smith', 1, 950, 100, 90, 80, 75, 8])),
            dict(zip(columns, ['Jamie Lee', 2, 920, 95, 85, 70, 65, 6])),
        ]},
        'fieldTypes': {**{c: 'percent' for c in [*DEFAULTS[1:], EXTRA]},
                       'Satisfaction Score': 'number', 'Completes': 'number'},
    }


class AdvisorDashboardTests(unittest.TestCase):
    def app(self, order=None):
        at = AppTest.from_file(str(APP))
        at.session_state['doc_advisors'] = advisor_doc()
        at.session_state['advisor_metric_order'] = order
        at.run()
        self.assertEqual(len(at.exception), 0)
        return at

    def headers(self, at):
        return [m.value for m in at.markdown if 'class="advisor-row-header"' in m.value]

    def test_edit_opens_one_advisor_preview_and_preserves_expansion(self):
        at = self.app()
        expand = next(b for b in at.button if (b.key or '').startswith('expand_'))
        expand.click().run()
        expanded = set(at.session_state['expanded_rows'])
        edit = [b for b in at.button if b.label == 'Edit cards']
        self.assertEqual(len(edit), 1, 'Advisors needs a small shared Edit cards control')
        edit[0].click().run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(set(at.session_state['expanded_rows']), expanded)
        self.assertEqual(len(at.get('component_instance')), 1)

    def test_saved_metric_selection_applies_to_every_advisor(self):
        order = [EXTRA, DEFAULTS[2], DEFAULTS[0], 'Completes', *DEFAULTS[1:2], DEFAULTS[3]]
        at = self.app(order)
        headers = self.headers(at)
        self.assertEqual(len(headers), 2)
        for header in headers:
            for metric in order[:4]:
                self.assertIn(metric, header, 'Saved summary metrics must render on every advisor')
            positions = [header.index(metric) for metric in order[:4]]
            self.assertEqual(positions, sorted(positions))
            self.assertNotIn('Fixed right first time', header)
            self.assertNotIn('Kept informed', header)
        self.assertIn('75.0%', headers[0])
        self.assertIn('65.0%', headers[1])

    def send_editor_event(self, at, action, order):
        session = at.session_state['advisor_layout_edit_session']
        at.session_state['advisor_layout_editor_' + session] = {
            'action': action, 'order': order, 'session_id': session,
            'event_id': uuid4().hex,
        }
        at.run()
        self.assertEqual(len(at.exception), 0)

    def test_cancel_discards_draft_and_keeps_saved_layout(self):
        at = self.app(DEFAULTS + [EXTRA, 'Completes'])
        at.button(key='edit_advisor_cards').click().run()
        with patch('advisor_layout.save_metric_order') as save:
            self.send_editor_event(at, 'cancel', [EXTRA, *DEFAULTS, 'Completes'])
            save.assert_not_called()
        self.assertIsNone(at.session_state['advisor_layout_edit_session'])
        self.assertEqual(at.session_state['advisor_metric_order'][:4], DEFAULTS)
        self.assertNotIn(EXTRA, self.headers(at)[0])

    def test_save_persists_layout_and_updates_all_advisors(self):
        order = [EXTRA, *DEFAULTS, 'Completes']
        at = self.app()
        at.button(key='edit_advisor_cards').click().run()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'advisor_layout.json'
            with patch('advisor_layout.save_metric_order',
                       side_effect=lambda _, value: save_metric_order(path, value)):
                self.send_editor_event(at, 'save', order)
            self.assertEqual(load_metric_order(path), order)
            with patch('advisor_layout.load_metric_order', return_value=load_metric_order(path)):
                reloaded = AppTest.from_file(str(APP))
                reloaded.session_state['doc_advisors'] = advisor_doc()
                reloaded.run()
                self.assertEqual(reloaded.session_state['advisor_metric_order'], order)
                self.assertTrue(all(EXTRA in h for h in self.headers(reloaded)))
        self.assertIsNone(at.session_state['advisor_layout_edit_session'])
        self.assertTrue(all(EXTRA in h for h in self.headers(at)))

    def test_failed_save_keeps_editor_and_original_layout(self):
        at = self.app(DEFAULTS + [EXTRA, 'Completes'])
        at.button(key='edit_advisor_cards').click().run()
        with patch('advisor_layout.save_metric_order', side_effect=OSError('read only')):
            self.send_editor_event(at, 'save', [EXTRA, *DEFAULTS, 'Completes'])
        self.assertIsNotNone(at.session_state['advisor_layout_edit_session'])
        self.assertEqual(at.session_state['advisor_metric_order'][:4], DEFAULTS)
        self.assertEqual(len(at.error), 1)
        self.assertIn('Could not save', at.error[0].value)

    def test_failed_save_is_not_replayed_by_an_unrelated_rerun(self):
        at = self.app(DEFAULTS + [EXTRA, 'Completes'])
        at.button(key='edit_advisor_cards').click().run()
        with patch('advisor_layout.save_metric_order', side_effect=OSError('read only')):
            self.send_editor_event(at, 'save', [EXTRA, *DEFAULTS, 'Completes'])
        key = 'advisor_layout_editor_' + at.session_state['advisor_layout_edit_session']
        # AppTest cannot replay a custom-component widget itself; a live browser
        # retains its last returned value until the next component submission.
        last_event = at.session_state[key]
        with patch('advisor_layout.save_metric_order') as save:
            at.session_state[key] = last_event
            next(b for b in at.button if (b.key or '').startswith('expand_')).click().run()
            save.assert_not_called()
        self.assertIsNotNone(at.session_state['advisor_layout_edit_session'])
        with patch('advisor_layout.save_metric_order') as save:
            self.send_editor_event(at, 'save', [EXTRA, *DEFAULTS, 'Completes'])
            save.assert_called_once()
        self.assertIsNone(at.session_state['advisor_layout_edit_session'])

    def test_promoted_text_metrics_are_escaped(self):
        doc = advisor_doc()
        doc['dataset']['columns'].append('Customer <note>')
        doc['dataset']['rows'][0]['Customer <note>'] = '<img src=x onerror=alert(1)>'
        at = AppTest.from_file(str(APP))
        at.session_state['doc_advisors'] = doc
        at.session_state['advisor_metric_order'] = ['Customer <note>', *DEFAULTS]
        at.run()
        header = self.headers(at)[0]
        self.assertIn('Customer &lt;note&gt;', header)
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', header)
        self.assertNotIn('<img', header)


if __name__ == '__main__':
    unittest.main()
