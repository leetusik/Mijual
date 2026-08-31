# Deferred: D37 404가 한글 주소를 퍼센트 인코딩된 채로 보여준다

## Context

## Why Deferred

usePathname() returns the encoded pathname, so 「/어디에도-없는-주소」 reads /%EC%96%B4… on the one screen whose job is to echo the reader's own address — on a Korean-only product.

## Trigger to Promote

The next 404/error-surface work (natural pair with D35), or before the P4 demo

## Notes

