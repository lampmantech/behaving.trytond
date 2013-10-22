;;; -*- encoding: utf-8 -*-
;; Quick and dirty hack to convert an Emacs buffer
;; of trytond doctest rst into behave feature file
;; No comments please on the code quality!

(defun rst_to_feature ()
  (interactive)
  (let ((beg (if (and transient-mark-mode mark-active) (region-beginning)))
	(end (if (and transient-mark-mode mark-active) (region-end))))
    (goto-char (point-min))
    (replace-regexp "^    >>> \\(.+\\)
    True" "    assert \\1" nil beg end)
    (goto-char (point-min))
    (replace-regexp "^    >>> \\(.+\\)
    False" "    assert not \\1" nil beg end)
    (goto-char (point-min))
    (replace-regexp "^    >>> \\(.+\\)
    \\([0-9]+\\)" "    assert \\1 == \\2" nil beg end)
    (goto-char (point-min))
    (replace-regexp "^    >>> " "    " nil beg end)
    (goto-char (point-min))
    (replace-regexp "^    \\.\\.\\. " "        " nil beg end)
    (goto-char (point-min))
    ;; are these always single lines?
    (replace-regexp "^\\([A-Za-z].*\\)::" "@step('\\1')\ndef step_impl(context):" nil beg end)

    )
  )