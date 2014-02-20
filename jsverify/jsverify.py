
import re
import struct

lexer_debug = False

#--------------------------------------------------------------------

class Token:

    stock_SimpleTextLine = struct.pack("ii",0,0)
        
    @staticmethod
    def pack( tokens ):
        if tokens == [(0,0)]:
            #print( "simple text line", id(Token.stock_SimpleTextLine) )
            return Token.stock_SimpleTextLine
        s = b""
        for token in tokens:
            s += struct.pack("ii",token[0],token[1])
        return s

    @staticmethod
    def unpack( s ):
        tokens = []
        for i in range( 0, len(s), 8 ):
            tokens.append( struct.unpack( "ii", s[i:i+8] ) )
        return tokens

Token_Text = 0
Token_Keyword = 1
Token_Name = 2
Token_Number = 3
Token_String = 4
Token_Preproc = 5
Token_Comment = 6
Token_Space = 7
Token_Error = -1

def rootContext():
    return 'root'

## シンタックス分析クラスのベースクラス
class Lexer:

    def __init__(self):
        pass

    def lex( self, ctx, line, detail ):
        pass

## テキストファイル用のシンタックス分析クラス
class TextLexer(Lexer):
    def __init__(self):
        Lexer.__init__(self)

    def lex( self, ctx, line, detail ):
        if detail:
            return [ (0,Token_Text) ], ctx
        else:
            return ctx

## 正規表現のテーブルを使ったシンタックス分析クラスのベースクラス
class RegexLexer(Lexer):

    Detail = 1<<0  # detailモードの場合のみ使用するルール

    def __init__(self):
        Lexer.__init__(self)
        self.rule_map = {}
        self.rule_map_ctx = {}
        self.re_flags = 0
        self.compiled = False

    def _compile(self):
    
        for k in self.rule_map.keys():
            rule_list = self.rule_map[k]
            for i in range(len(rule_list)):
                rule = rule_list[i]
                rule = list(rule)
                if len(rule)<=2:
                    rule.append(None)
                if len(rule)<=3:
                    rule.append(0)
                if rule[0]!=None:
                    rule[0] = re.compile( rule[0], self.re_flags )
                rule_list[i] = rule
                
                assert( not( isinstance( rule[2], tuple ) or isinstance( rule[2], list ) ) )
                
                if rule[0]==None or (rule[3] & RegexLexer.Detail)==0:
                    if not k in self.rule_map_ctx:
                        self.rule_map_ctx[k] = []
                    self.rule_map_ctx[k].append(rule)

        self.compiled = True

    def lex( self, ctx, line, detail ):
    
        if not self.compiled:
            self._compile()
    
        if lexer_debug:
            print( "line :", line )

        tokens = []
        pos = 0
        
        def getRuleList():
            if detail:
                return self.rule_map[ctx]
            else:
                return self.rule_map_ctx[ctx]

        rule_list = getRuleList()

        while pos<=len(line):

            if lexer_debug:
                print( "  context :", ctx )
                
            last = pos==len(line)

            nearest_rule = None
            nearest_result = None
            default_rule = None

            for rule in rule_list:

                if rule[0]!=None:
                    re_result = rule[0].search( line, pos )
                    if re_result:
                        if nearest_result==None or re_result.start()<nearest_result.start():
                            nearest_result = re_result
                            nearest_rule = rule
                            if re_result.start()==pos:
                                break
                else:
                    default_rule = rule
                    break
                
            else:
                if pos<len(line):
                    tokens.append( ( pos, Error ) )
                break
                
            if lexer_debug:
                print( "  nearest_rule :", nearest_rule )
                print( "  default_rule :", default_rule )

            if default_rule:
                if len(tokens)==0 or tokens[-1][1]!=default_rule[1]:
                    if pos<len(line):
                        if lexer_debug:
                            print( "  %d, %d (default rule)" % (pos, default_rule[1]) )
                        tokens.append( ( pos, default_rule[1] ) )

            if nearest_rule:

                pos = nearest_result.start()
                rule = nearest_rule

                if isinstance( rule[1], tuple ) or isinstance( rule[1], list ):
                    action_list = rule[1]
                    for i in range(len(action_list)):
                        if len(tokens)==0 or tokens[-1][1]!=action_list[i]:
                            if pos<len(line):
                                if lexer_debug:
                                    print( "  %d, %d (group %d)" % (pos, action_list[i], i) )
                                tokens.append( ( pos, action_list[i] ) )
                        pos += len( nearest_result.group(i+1) )

                else:
                    if len(tokens)==0 or tokens[-1][1]!=rule[1]:
                        if pos<len(line):
                            if lexer_debug:
                                print( "  %d, %d" % (pos, rule[1]) )
                            tokens.append( ( pos, rule[1] ) )
                    pos += len( nearest_result.group(0) )

            if rule[2]:
                ctx = rule[2]
                rule_list = getRuleList()
                if lexer_debug:
                    print( "  context ->", ctx )
                    
            if default_rule and not nearest_rule:
                break
                    
            if last:
                break

        if detail:
            return tokens, ctx
        else:
            return ctx


#--------------------------------------------------------------------


## JavaScript のシンタックス解析クラス
class JavaScriptLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)

        self.rule_map['multiline_comment'] = [
            (r'[*]/', Token_Comment, 'root'),
            (None, Token_Comment),
        ]

        # FIXME : 正規表現リテラルをちゃんと扱う

        """
        self.rule_map['slashstartsregex'] = [
            (r'\s+', Token_Text),
            (r'<!--', Token_Comment),
            (r'//.*$', Token_Comment, 'root'),
            (r'/[*]', Token_Comment, 'multiline_comment'),
            (r'/(\\.|[^[/\\\n]|\[(\\.|[^\]\\\n])*])+/'
             r'([gim]+\b|\B)', Token_String, 'root'),
            #(r'(?=/)', Token_Text, 'root'),
            (None, Token_Text, 'root'),
        ]
        """

        self.rule_map['root'] = [
            #(r'^(?=\s|/|<!--)', Token_Text, 'slashstartsregex'), 
            (r'\s+', Token_Text),
            (r'<!--', Token_Comment),
            (r'//.*$', Token_Comment),
            (r'/[*]', Token_Comment, 'multiline_comment'),
            #(r'\+\+|--|~|&&|\?|:|\|\||\\(?=\n)|'
            # r'(<<|>>>?|==?|!=?|[-<>+*%&\|\^/])=?', Token_Text, 'slashstartsregex'),
            #(r'[{(\[;,]', Token_Text, 'slashstartsregex'),
            (r'[})\].]', Token_Text),

            (r'(eval)\b', Token_Error, None, RegexLexer.Detail),

            (r'(for|in|while|do|break|return|continue|switch|case|default|if|else|'
             r'throw|try|catch|finally|new|delete|typeof|instanceof|void|'
             r'this)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'(var|with|function)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'(abstract|boolean|byte|char|class|const|debugger|double|enum|export|'
             r'extends|final|float|goto|implements|import|int|interface|long|native|'
             r'package|private|protected|public|short|static|super|synchronized|throws|'
             r'transient|volatile)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'(true|false|null|NaN|Infinity|undefined)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'(Array|Boolean|Date|Error|Function|Math|netscape|'
             r'Number|Object|Packages|RegExp|String|sun|decodeURI|'
             r'decodeURIComponent|encodeURI|encodeURIComponent|'
             r'Error|isFinite|isNaN|parseFloat|parseInt|document|this|'
             r'window)\b', Token_Name, None, RegexLexer.Detail),
            (r'[$a-zA-Z_][a-zA-Z0-9_]*', Token_Text),
            (r'[0-9][0-9]*\.[0-9]+([eE][0-9]+)?[fd]?', Token_Number, None, RegexLexer.Detail),
            (r'0x[0-9a-fA-F]+', Token_Number, None, RegexLexer.Detail),
            (r'[0-9]+', Token_Number, None, RegexLexer.Detail),
            (r'"(\\\\|\\"|[^"])*"', Token_String),
            (r"'(\\\\|\\'|[^'])*'", Token_String),
            (None,Token_Text)
        ]

#----------------------------------------------------------

def main():
    
    ctx = rootContext()
    
    if 0:
        lexer = PythonLexer()
        lines = [
        
            "import os",
            "import sys",
        
            "'''",
            "abc",
            "'''",
        ]
        
    if 1:
        lexer = JavaScriptLexer()
        lines = [
            'var a = 1;',
            'eval( "a=2;" );',
        ]
    
    error_detected = False
    
    for line in lines:
        
        tokens, ctx = lexer.lex( ctx, line, True )
    
        for i in range(len(tokens)):
            pos1 = tokens[i][0]
            if i+1 < len(tokens):
                pos2 = tokens[i+1][0]
            else:
                pos2 = len(line)
            print( "  %s %s" % ( tokens[i][1], line[pos1:pos2] ) )

            if tokens[i][1] == Token_Error:
                error_detected = True

    if error_detected:
        print "error detected !"

main()

