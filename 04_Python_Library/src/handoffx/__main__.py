"""Command-line recommendation.

    python -m handoffx --continue-success .8 --retry-success .6 --human-success .9 \
        --history continue:hard_failure,retry:hard_failure
"""
from __future__ import annotations
import argparse
from .advisor import Advisor, Costs


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog='handoffx', description='Recommend continue / retry / human / stop.')
    ap.add_argument('--continue-success', type=float, default=.8)
    ap.add_argument('--retry-success', type=float, default=.6)
    ap.add_argument('--human-success', type=float, default=.9)
    ap.add_argument('--uncertainty', type=float, default=.15, help='absolute uncertainty of the estimates')
    ap.add_argument('--human-cost', type=float, default=4.)
    ap.add_argument('--failure-loss', type=float, default=18.)
    ap.add_argument('--stop-loss', type=float, default=12.)
    ap.add_argument('--no-human', action='store_true', help='human assistance unavailable')
    ap.add_argument('--history', default='', help='comma-separated action:outcome pairs for this episode')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    adv = Advisor.from_estimates(a.continue_success, a.retry_success, a.human_success, a.uncertainty,
                                 costs=Costs(human=a.human_cost, failure=a.failure_loss, stop=a.stop_loss),
                                 human_available=not a.no_human)
    hist = [tuple(x.split(':', 1)) for x in a.history.split(',') if x]
    rec = adv.recommend(hist)
    print(rec.to_json() if a.json else rec.explain())


if __name__ == '__main__':
    main()
