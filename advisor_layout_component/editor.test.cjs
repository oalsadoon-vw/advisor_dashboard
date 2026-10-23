const test = require('node:test');
const assert = require('node:assert/strict');
const { normalizeOrder, moveToGap, dragScrollSpeed } = require('./editor.js');

test('normalization retains available metric order and appends new metrics once', () => {
  assert.deepEqual(normalizeOrder(['c', 'unknown', 'c', 'a'], ['a', 'b', 'c', 'd']), ['c', 'a', 'b', 'd']);
});

test('a card can move from expanded details into the first four positions', () => {
  assert.deepEqual(moveToGap(['a', 'b', 'c', 'd', 'e', 'f'], 'f', 1), ['a', 'f', 'b', 'c', 'd', 'e']);
});

test('a card can move from the collapsed row into expanded details', () => {
  assert.deepEqual(moveToGap(['a', 'b', 'c', 'd', 'e', 'f'], 'b', 6), ['a', 'c', 'd', 'e', 'f', 'b']);
});

test('dropping beside the original position leaves the order unchanged', () => {
  const order = ['a', 'b', 'c'];
  assert.deepEqual(moveToGap(order, 'b', 1), order);
  assert.deepEqual(moveToGap(order, 'b', 2), order);
  assert.deepEqual(order, ['a', 'b', 'c']);
});

test('invalid moves leave the current order intact', () => {
  assert.deepEqual(moveToGap(['a', 'b'], 'missing', 0), ['a', 'b']);
  assert.deepEqual(moveToGap(['a', 'b'], 'b', null), ['a', 'b']);
});

test('dragging toward either pane edge scrolls toward cards beyond that edge', () => {
  const pane = { left: 10, right: 310, top: 100, bottom: 500, height: 400 };
  assert.ok(dragScrollSpeed(150, 108, pane) < 0);
  assert.ok(dragScrollSpeed(150, 492, pane) > 0);
  assert.ok(Math.abs(dragScrollSpeed(150, 108, pane)) > Math.abs(dragScrollSpeed(150, 140, pane)));
});

test('drag scrolling stops away from the edge or outside the card pane', () => {
  const pane = { left: 10, right: 310, top: 100, bottom: 500, height: 400 };
  assert.equal(dragScrollSpeed(150, 300, pane), 0);
  assert.equal(dragScrollSpeed(9, 108, pane), 0);
  assert.equal(dragScrollSpeed(150, 99, pane), 0);
  assert.equal(dragScrollSpeed(311, 492, pane), 0);
  assert.equal(dragScrollSpeed(150, 501, pane), 0);
});
