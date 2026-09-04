# Interface Copy: Simplified Chinese Profile

Apply the shared interface-content standard first. This profile contains only Simplified Chinese decisions.

## 1. Syntax and Address

- Omit the subject when context is clear. Choose either “你” or “您” for the product and do not mix them.
- Use “我们” only when the product team assumes responsibility, offers support, reviews feedback, or needs a real conversational relationship. State ordinary results directly.
- Avoid bureaucratic language, rare words, excessive colloquialism, system-centric phrasing, and long stacks of nouns.
- Describe an objective failed result rather than blaming the user. A safety prohibition may be direct but must explain the reason or feasible path.

## 2. Punctuation, Numbers, and Length

- Use full-width Chinese punctuation for complete sentences and paragraphs; keep quotation marks, brackets, ellipses, and connectors consistent with the project typography.
- Do not use exclamation marks for ordinary success, loading, or guidance. Reserve them for genuine greetings, congratulations, or strong warnings.
- State dates, times, quantities, units, and ranges with an explicit basis. Follow the project's spacing system for Chinese, Latin text, numbers, and units.
- Set no universal Chinese character limit. Preserve action, consequence, and recovery before fitting component space; shorter Chinese does not justify less information.

## 3. Localization

Translate complete-message intent, never word by word or by runtime concatenation. Variable order, classifiers, and subject omission differ from English, so retain a complete template per language.

`Continue` may become “继续,” “下一步,” “开始生成,” or the concrete submit action. `Got it` may become “知道了” or need no button. Choose from the actual outcome.
