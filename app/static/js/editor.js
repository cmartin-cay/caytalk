$(function() { $('textarea').froalaEditor({
    heightMin: 180,
    heightMax: 180,
    placeholderText: "",
    toolbarButtons: ['bold', 'italic', 'underline', 'emoticons', '|', 'strikeThrough', 'superscript','subscript', 'html'],
    pluginsEnabled: ['url', 'emoticons', 'link', 'codeView'],
    linkAlwaysBlank: true,
    enter: $.FroalaEditor.ENTER_BR
})
});

// $('.selector').froalaEditor('link.insert', {'target': '_blank'});
